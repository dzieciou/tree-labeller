import csv
import glob
import logging
import os
import re
from typing import Set, Dict, Iterable

from tree_labeller.core.types import Label, ProductId, LabelableCategory, Product
from tree_labeller.core.utils import remove_leaf_categories_without_product
from tree_labeller.parsers.yaml import YamlTreeParser


def _parse_path(path: str) -> int:
    fname = os.path.basename(path)
    m = re.match(
        r"(?P<iteration>\d+)-(to-verify|good).tsv",
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


class LabelingState:
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
        tree = YamlTreeParser().parse_tree(tree_path)
        remove_leaf_categories_without_product(tree)

        iteration = 0
        paths = glob.glob(os.path.join(dir, "*.tsv"))
        if paths:
            path = max(paths, key=os.path.getctime)
            labels = _load_labels(path, allowed_labels)
            _update_tree(tree, labels)
            iteration = _parse_path(path)

        return LabelingState(tree, iteration)

    def save_to_verify(self, path: str):
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

        with open(path, "w") as f:
            writer = csv.DictWriter(
                f,
                delimiter="\t",
                fieldnames=self._get_fieldnames(to_verify),
            )
            writer.writeheader()

            for product in to_verify:
                writer.writerow(
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category_name,
                        "label": "|".join(sorted(product.labels.to_verify)),
                        **product.attrs,
                    }
                )

    def save_good_predicted_labels(self, path: str):
        products_with_good_labels = [
            product for product in self.tree.products if product.labels.is_good
        ]
        with open(path, "w") as f:
            writer = csv.DictWriter(
                f,
                delimiter="\t",
                fieldnames=self._get_fieldnames(products_with_good_labels),
            )
            writer.writeheader()
            for product in products_with_good_labels:
                writer.writerow(
                    {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category_name,
                        "label": product.labels.good_label,
                        **product.attrs,
                    }
                )

    def _get_fieldnames(self, products: Iterable[Product]):
        attr_names = set(
            attr_name for product in products for attr_name in product.attrs.keys()
        )
        return ["id", "name", *sorted(attr_names), "category", "label"]

    def get_category(self, category_id: int):
        return self._categories_by_id[int(category_id)]

    def get_product(self, product_id: int):
        return self._products_by_id[int(product_id)]
