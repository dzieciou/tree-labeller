import csv
import glob
import itertools
import json
import logging
import os.path
import re
import shutil
from collections import Counter
from datetime import datetime
from typing import Iterable, Set, Optional, Dict, List

import yaml
from jsonlines import jsonlines
from tabulate import tabulate
from termgraph.termgraph import chart, AVAILABLE_COLORS

from labeller.labelled_tree import (
    remove_leaf_categories_without_product,
)
from labeller.parsers.yaml import YamlTreeParser
from labeller.types import (
    TO_REJECT_LABEL,
    TO_SKIP_LABEL,
    ProductId,
    Label,
    Category,
    Product,
)

CONFIGURATION_FILE = "config.yaml"

START_TIME_FORMAT = "%Y%m%d%H%M%S"


def load_labels(tsv_path: str, allowed_labels: Set[Label]) -> Dict[ProductId, Label]:
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


def update_tree(tree: Category, labels: Set[Label]):
    products_by_id = {int(product.id): product for product in tree.leaves}
    for product_id, label in labels.items():
        product = products_by_id[product_id]
        product.labels.manual = label


def parse_path(path: str):
    fname = os.path.basename(path)
    m = re.match(
        r"(?P<iteration>\d+)-(to-verify|good-labels).tsv",
        fname,
    )
    assert m is not None
    path_parts = m.groupdict()
    iteration = int(path_parts["iteration"])
    return iteration


class LabellingTask:
    @classmethod
    def initialize(
        cls, dir: str, tree_path: str, allowed_labels: Set[Label]
    ) -> "LabellingTask":
        dir = os.path.abspath(dir)
        try:
            os.makedirs(dir, exist_ok=False)
        except FileExistsError:
            print(f"Directory {dir} already exists. Perhaps this is a previous task?")
            return

        dest_tree_path = os.path.join(dir)
        shutil.copy(tree_path, dest_tree_path)

        return cls.from_dir(dir)

    @classmethod
    def from_dir(cls, dir: str) -> "LabellingTask":
        with open(os.path.join(dir, CONFIGURATION_FILE)) as f:
            config = yaml.safe_load(f)

        allowed_provided_labels = set(config["allowed_labels"])
        start_time = config["start_time"]
        unique_labels = set(allowed_provided_labels)
        assert len(unique_labels) == len(
            allowed_provided_labels
        ), f"Redundant labels in: {allowed_provided_labels}"
        allowed_labels = unique_labels | {TO_REJECT_LABEL, TO_SKIP_LABEL}

        tree_path = os.path.join(dir, config["tree"])
        tree, _ = YamlTreeParser().parse_tree(tree_path)

        iteration = 0
        paths = glob.glob(os.path.join(dir, "*.tsv"))
        if paths:
            path = max(paths, key=os.path.getctime)
            labels = load_labels(path, allowed_labels)
            update_tree(tree, labels)
            last_iteration = parse_path(path)
            iteration = last_iteration + 1

        task = LabellingTask(
            dir, tree, allowed_provided_labels, allowed_labels, start_time, iteration
        )
        return task

    def __init__(
        self,
        dir: str,
        tree: Category,
        allowed_provided_labels: Set[str],
        allowed_labels: Set[str],
        start_time: datetime = None,
        iteration: int = 0,
    ):

        remove_leaf_categories_without_product(tree)

        assert dir != None
        assert os.path.isdir(dir)
        assert tree != None

        self.dir = dir
        self.tree = tree
        self.allowed_provided_labels = allowed_provided_labels
        self.allowed_labels = allowed_labels
        self.start_time: datetime = start_time or datetime.now()
        self.iteration: int = iteration

        self._categories_by_id = {
            int(category.id): category for category in self.tree.categories
        }
        self._products_by_id = {
            int(product.id): product for product in self.tree.products
        }

    def save_config(self):
        config = {
            "dir": dir,
            "tree": self.tree_path,
            "allowed_provided_labels": list(self.allowed_provided_labels),
            "start_time": self.start_time,
        }
        with open(os.path.join(dir, CONFIGURATION_FILE), "w") as out:
            yaml.dump(config, out)

    @property
    def n_products(self):
        return self.tree.n_products

    @property
    def n_categories(self):
        return self.tree.n_categories

    def get_category(self, category_id: int):
        return self._categories_by_id[int(category_id)]

    def get_product(self, product_id: int):
        return self._products_by_id[int(product_id)]

    def init_manual_labels(self):
        if os.path.isdir(self.dir):

            if not paths:
                self._start_labelling()
            else:

                self.load_manual_labels(path)

    def load_manual_labels(self, path: str):
        labels = self.load_labels(path)
        dir, _, content_hash, start, iteration = self.parse_path(path)
        self.set_manual_labels(dir, start, iteration, labels)

    def set_manual_labels(
        self, start: datetime, iteration: int, labels: Dict[ProductId, Label]
    ):
        self.start_time = start
        self.iteration = iteration + 1  # Let's prepare for the next iteration...

    def try_save_labels_to_verify(self, path: Optional[str] = None) -> Optional[str]:

        if self.n_selected_for_verification_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                self.content_hash,
                self.start_time,
                self.iteration,
                "to-verify",
                "tsv",
            )

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

        return path

    def try_save_good_predicted_labels(
        self, path: Optional[str] = None
    ) -> Optional[str]:

        if self.n_good_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                self.content_hash,
                self.start_time,
                self.iteration,
                "good-labels",
                "tsv",
            )
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
        return path

    def to_path(
        self,
        content_hash: str,
        starttime: datetime,
        iteration: int,
        suffix: str,
        extension: str,
    ):
        fname = f"{content_hash}-{starttime.strftime(START_TIME_FORMAT)}-{iteration}-{suffix}.{extension}"
        return os.path.join(self.dir, fname)

    def _start_labelling(self):
        self.start_time = datetime.now()
        self.iteration = 1

    @property
    def shop_stats(self):
        n_categories_per_depth = Counter(
            category.depth for category in self.tree.categories
        )
        n_categories_per_depth = {
            depth: n_categories
            for depth, n_categories in n_categories_per_depth.most_common()
        }
        return {
            "n_products": self.tree.n_products,
            "n_categories": self.tree.n_categories,
            "n_categories_per_depth": n_categories_per_depth,
        }

    @property
    def manual_labels_stats(self):
        return {
            "n_manual_labels": self.n_manual_labels,
            "n_allowed_labels_used": self.n_allowed_labels_used,
            "allowed_labels_not_used": self.allowed_labels_not_used,
            "n_allowed_labels": self.n_allowed_labels,
            "n_products_per_manual_label": self.n_products_per_manual_label,
        }

    @property
    def n_allowed_labels_used(self):
        return len(self.allowed_labels_used)

    @property
    def n_allowed_provided_labels_used(self):
        return len(self.allowed_provided_labels_used)

    @property
    def allowed_labels_used(self):
        return set(
            product.labels.manual
            for product in self.tree.products
            if product.labels.manual and product.labels.manual in self.allowed_labels
        )

    @property
    def allowed_provided_labels_used(self):
        return set(
            product.labels.manual
            for product in self.tree.products
            if product.labels.manual
            and product.labels.manual in self.allowed_provided_labels
        )

    @property
    def allowed_labels_not_used(self) -> Set[str]:
        return self.allowed_labels - self.allowed_labels_used

    @property
    def allowed_provided_labels_not_used(self) -> Set[str]:
        return self.allowed_provided_labels - self.allowed_provided_labels_used

    @property
    def n_allowed_labels(self):
        return len(self.allowed_labels) if self.allowed_labels else None

    @property
    def n_allowed_provided_labels(self):
        return (
            len(self.allowed_provided_labels) if self.allowed_provided_labels else None
        )

    @property
    def n_products_per_manual_label(self):
        n_products_per_manual_label = Counter(
            product.labels.manual
            for product in self.tree.products
            if product.labels.manual is not None
        )
        if self.allowed_labels:
            for label in self.allowed_labels:
                if label not in n_products_per_manual_label:
                    n_products_per_manual_label[label] = 0
        return {
            label: n_products
            for label, n_products in n_products_per_manual_label.most_common()
        }

    @property
    def n_products_per_ambiguous_label(self):
        ambiguous_labels = itertools.chain.from_iterable(
            product.labels.ambiguous
            for product in self.tree.products
            if product.labels.is_ambiguous
        )

        n_products_per_ambiguous_label = Counter(ambiguous_labels)
        if self.allowed_labels:
            for label in self.allowed_labels:
                if label not in n_products_per_ambiguous_label:
                    n_products_per_ambiguous_label[label] = 0
        return {
            label: n_products
            for label, n_products in n_products_per_ambiguous_label.most_common()
        }

    @property
    def n_products_per_good_label(self):
        n_products_per_good_label = Counter(
            product.labels.good_label
            for product in self.tree.products
            if product.labels.is_good
        )
        if self.allowed_labels:
            for label in self.allowed_labels:
                if label not in n_products_per_good_label:
                    n_products_per_good_label[label] = 0
        return {
            label: n_products
            for label, n_products in n_products_per_good_label.most_common()
        }

    @property
    def predicted_labels_stats(self):
        return {
            "n_good_labels": self.n_good_labels,
            "n_unique_good_labels": len(
                set(
                    product.labels.good_label
                    for product in self.tree.products
                    if product.labels.is_good
                )
            ),
            "n_missing_labels": self.n_missing_labels,
            "n_to_reject_labels": self.n_to_reject_labels,
            "n_to_skip_labels": self.n_to_skip_labels,
            "n_ambiguous_labels": self.n_ambiguous_labels,
            "n_requires_verification_labels": self.n_requires_verification_labels,
            "n_requires_verification_missing_labels": self.n_required_verification_missing_labels,
            "n_requires_verification_ambiguous_labels": self.n_requires_verification_ambiguous_labels,
            "n_selected_for_verification_labels": self.n_selected_for_verification_labels,
            "n_selected_for_verification_missing_labels": self.n_selected_for_verification_missing_labels,
            "n_selected_for_verification_ambiguous_labels": self.n_selected_for_verification_ambiguous_labels,
        }

    @property
    def n_selected_for_verification_ambiguous_labels(self):
        return sum(
            1
            for product in self.tree.products
            if product.labels.selected and product.labels.is_ambiguous
        )

    @property
    def n_selected_for_verification_missing_labels(self):
        return sum(
            1
            for product in self.tree.products
            if product.labels.selected and product.labels.is_missing
        )

    @property
    def n_selected_for_verification_labels(self):
        return sum(1 for product in self.tree.products if product.labels.selected)

    @property
    def n_requires_verification_ambiguous_labels(self):
        return sum(
            1
            for product in self.tree.products
            if product.labels.requires_verification() and product.labels.is_ambiguous
        )

    @property
    def n_required_verification_missing_labels(self):
        return sum(
            1
            for product in self.tree.products
            if product.labels.requires_verification() and product.labels.is_missing
        )

    @property
    def n_requires_verification_labels(self):
        return sum(
            1
            for product in self.tree.products
            if product.labels.requires_verification()
        )

    @property
    def n_ambiguous_labels(self):
        return sum(1 for product in self.tree.products if product.labels.is_ambiguous)

    @property
    def n_missing_labels(self):
        return sum(1 for product in self.tree.products if product.labels.is_missing)

    @property
    def n_to_reject_labels(self):
        return sum(1 for product in self.tree.products if product.labels.to_reject)

    @property
    def n_to_skip_labels(self):
        return sum(1 for product in self.tree.products if product.labels.to_skip)

    @property
    def n_good_labels(self):
        return sum(1 for product in self.tree.products if product.labels.is_good)

    @property
    def stats(self):
        return {
            "shop": self.shop_stats,
            "manual_labels": self.manual_labels_stats,
            "predicted_labels": self.predicted_labels_stats,
            "progress": self.progress,
        }

    @property
    def n_manual_labels(self):
        return sum(1 for product in self.tree.products if product.labels.manual)

    def save_stats(self, path: Optional[str] = None):
        if path is None:
            path = self.to_path(
                self.content_hash,
                self.start_time,
                self.iteration,
                "stats",
                "json",
            )
        with open(path, "w") as f:
            json.dump(self.stats, f, indent=2, cls=CustomEncoder)
        logging.info(f"Saved stats to {path}.")

    @property
    def progress(self):
        return {
            "manual": self.n_manual_labels,
            "univocal": self.n_good_labels / self.n_products,
            "ambiguous": self.n_ambiguous_labels / self.n_products,
            "missing": self.n_missing_labels / self.n_products,
            "allowed_labels": self.n_allowed_provided_labels_used
            / self.n_allowed_provided_labels,
        }

    def update_all_stats(self, path: Optional[str] = None):
        if path is None:
            path = self.all_stats_path

        iteration_stats = {
            "start_time": self.start_time.isoformat(),
            "iteration": self.iteration,
            "stats": self.stats,
        }
        encoder = CustomEncoder()
        with jsonlines.open(path, "a", dumps=encoder.encode) as writer:
            writer.write(iteration_stats)
        logging.info(f"Updated all iterations stats in {path}.")

    @property
    def all_stats_path(self):
        return self.to_path(
            self.content_hash,
            self.start_time,
            "all",
            "stats",
            "jsonl",
        )

    @property
    def progress_table(self):
        rows = []
        with jsonlines.open(self.all_stats_path) as reader:
            for iteration_stats in reader:
                row = [
                    iteration_stats["iteration"],
                    iteration_stats["stats"]["progress"]["manual"],
                    iteration_stats["stats"]["progress"]["univocal"],
                    iteration_stats["stats"]["progress"]["ambiguous"],
                    iteration_stats["stats"]["progress"]["missing"],
                    iteration_stats["stats"]["shop"]["n_products"],
                    iteration_stats["stats"]["progress"]["allowed_labels"],
                ]
                rows.append(row)

        return tabulate(
            rows,
            headers=[
                "Iteration",
                "Manual",
                "Univocal",
                "Ambiguous",
                "Missing",
                "Total",
                "Allowed Labels",
            ],
            floatfmt=".0%",
        )

    def print_manual_labels_coverage(self):
        coverage = sorted(
            self.n_products_per_manual_label.items(),
            key=lambda label_count: (label_count[1], label_count[0]),
        )
        labels = [get_label_name(label_count[0]) for label_count in coverage]
        data = [[label_count[1]] for label_count in coverage]
        args = {
            "histogram": False,
            "stacked": False,
            "different_scale": False,
            "width": 50,
            "no_labels": False,
            "no_values": False,
            "format": "{:.0f}",
            "suffix": "",
            "vertical": False,
        }
        chart([AVAILABLE_COLORS["blue"]], data, args, labels)

    def print_predicted_labels_coverage(self):
        good = self.n_products_per_good_label
        ambiguous = self.n_products_per_ambiguous_label
        coverage = {
            label: (good[label], ambiguous[label])
            for label in self.allowed_provided_labels | {TO_REJECT_LABEL}
        }
        coverage = sorted(
            coverage.items(),
            key=lambda label_count: (label_count[1][0], label_count[0]),
        )
        labels = [get_label_name(label_count[0]) for label_count in coverage]
        data = [[label_count[1][0], label_count[1][1]] for label_count in coverage]
        args = {
            "histogram": False,
            "stacked": True,
            "different_scale": False,
            "width": 50,
            "no_labels": False,
            "no_values": False,
            "format": "{:.0f}",
            "suffix": "",
            "vertical": False,
        }
        chart([AVAILABLE_COLORS["green"], AVAILABLE_COLORS["red"]], data, args, labels)


def save_products(products: Iterable[Product], path: str):
    products = sorted(products, key=lambda product: product.category_name)
    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=Product.fieldnames, delimiter="\t")
        writer.writeheader()
        for product in products:
            writer.writerow(product.asdict())


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def get_label_name(label: str) -> str:
    return {
        TO_REJECT_LABEL: f"({TO_REJECT_LABEL}) Rejected",
        TO_SKIP_LABEL: f"({TO_SKIP_LABEL}) Skipped",
    }.get(label, label)


def load_allowed_labels(path: str) -> List[str]:
    with open(path) as f:
        labels = [label.strip() for label in f.readlines()]
    return labels
