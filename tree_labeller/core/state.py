import csv
import glob
import logging
import os
import re
from typing import Set, Dict

from tree_labeller.core.types import Label, ProductId, LabelableCategory
from tree_labeller.parsers.yaml import YamlTreeParser


def _parse_path(path: str) -> int:
    fname = os.path.basename(path)
    m = re.match(
        r"(?P<iteration>\d+)-(to-verify|good-labels).tsv",
        fname,
    )
    assert m is not None
    path_parts = m.groupdict()
    iteration = int(path_parts["iteration"])
    return iteration


def _load_labels(tsv_path: str, allowed_labels: Set[Label]) -> Dict[ProductId, Label]:
    missing = 0
    selected = 0
    ambiguous = 0
    with open(tsv_path) as f:
        rows = csv.DictReader(f, delimiter="\t")
        labels = {}
        for row in rows:
            selected += 1
            product_id = row["product_id"]
            label = row["label"].strip()
            if not label:
                missing += 1
                continue
            label_candidates = set(label.split("|"))
            unknown_labels = label_candidates - allowed_labels
            assert (
                not unknown_labels
            ), f"Unknown label(s) {unknown_labels}, expected one of: {allowed_labels}"
            if len(label_candidates) > 1:
                ambiguous += 1
                continue
            labels[product_id] = next(iter(label_candidates))

    logging.info(f"Loaded manual labels from {tsv_path}.")

    if selected and missing:
        logging.warning(
            f"{missing} of {selected} products selected lack label. You don't need to label all "
            f"products if you are not sure but consider increasing a number of products to select"
            f"in the next iteration."
        )
    if selected and ambiguous:
        logging.warning(
            f"{ambiguous} of {selected} products still have ambiguous labels. You don't need to select "
            f"the right one but this might decrease classification accuracy."
        )

    return labels


def _update_tree(tree: LabelableCategory, labels: Set[Label]):
    products_by_id = {product.id: product for product in tree.leaves}
    for product_id, label in labels.items():
        product = products_by_id[product_id]
        product.labels.manual = label


def _remove_leaf_categories_without_product(root: LabelableCategory):
    removed = True
    n_removed = 0
    while removed:
        removed = False
        for leaf in root.leaves:
            if isinstance(leaf, LabelableCategory):
                leaf.parent = None
                removed = True
                n_removed += 1
    logging.debug(f"Removed {n_removed} categories without product.")


class LabellingState:
    tree: LabelableCategory
    iteration: int

    def __init__(self, tree: LabelableCategory, iteration: int):
        self.tree = tree
        self.iteration = iteration
        self._categories_by_id = {
            int(category.id): category for category in self.tree.categories
        }
        self._products_by_id = {
            int(product.id): product for product in self.tree.products
        }

    @classmethod
    def from_dir(cls, dir: str, tree_path: str, allowed_labels: Set[str]):
        tree, _ = YamlTreeParser().parse_tree(tree_path)
        _remove_leaf_categories_without_product(tree)

        iteration = 0
        paths = glob.glob(os.path.join(dir, "*.tsv"))
        if paths:
            path = max(paths, key=os.path.getctime)
            labels = _load_labels(path, allowed_labels)
            _update_tree(tree, labels)
            iteration = _parse_path(path)

        return LabellingState(tree, iteration)

    def save_to_verify(self, path: str):
        # TODO Make serialization/deserialization of tree to/from yaml and labels to/from TSV
        #      independent of whether we talk about books, products or whatever.
        #      Mandatory fields for product are: id, label, category/parent
        #      All other fields are optional (name, brand). They should be read from Product.__dict__
        #      Mandatory fields for category are: id, parent.
        #      All other fields are optional (name). They should be read from Category.__dict__
        #      Should we read it from all products or first one? Same for categories...
        #      This may require changing also parser to
        #       This will require changes to YAML parser
        with open(path, "w") as f:
            writer = csv.DictWriter(
                f,
                delimiter="\t",
                fieldnames=["product_id", "name", "brand", "category", "label"],
            )
            writer.writeheader()

            to_verify = [
                product
                for product in self.tree.products
                if product.labels.selected or product.labels.manual
            ]
            to_verify = sorted(
                to_verify,
                key=lambda product: (
                    -len(product.labels.to_verify),
                    sorted(product.labels.to_verify),
                ),
            )
            for product in to_verify:
                writer.writerow(
                    {
                        "product_id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category": product.category_name,
                        "label": "|".join(product.labels.to_verify),
                    }
                )

    def save_good_predicted_labels(self, path: str):
        with open(path, "w") as f:
            writer = csv.DictWriter(
                f,
                delimiter="\t",
                fieldnames=["product_id", "name", "brand", "category", "label"],
            )
            writer.writeheader()
            for product in self.tree.products:
                if product.labels.is_good:
                    writer.writerow(
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "brand": product.brand,
                            "category": product.category_name,
                            "label": next(iter(product.labels.predicted)),
                        }
                    )

    def get_category(self, category_id: int):
        return self._categories_by_id[int(category_id)]

    def get_product(self, product_id: int):
        return self._products_by_id[int(product_id)]
