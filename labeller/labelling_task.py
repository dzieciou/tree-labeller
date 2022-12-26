import csv
import glob
import itertools
import json
import logging
import os.path
import re
from collections import Counter
from datetime import datetime
from typing import Iterable, Set, Optional, Dict, List

from jsonlines import jsonlines
from tabulate import tabulate
from termgraph.termgraph import chart, AVAILABLE_COLORS

from labeller.labelled_tree import (
    remove_leaf_categories_without_product,
)
from labeller.types import TO_REJECT_LABEL, TO_SKIP_LABEL, ProductId, Label, Category, Product

START_TIME_FORMAT = "%Y%m%d%H%M%S"


class LabellingTask:
    def __init__(
        self, root: Category, content_hash: str, allowed_provided_labels: Set[str]
    ):

        remove_leaf_categories_without_product(root)

        self.root = root
        self.content_hash = content_hash

        self._categories_by_id = {
            int(category.id): category for category in self.root.categories
        }
        self._products_by_id = {
            int(product.id): product for product in self.root.products
        }

        self.labelling_start: datetime = None
        self.labelling_iteration: int = None
        self.labelling_dir: str = None

        unique_labels = set(allowed_provided_labels)
        assert len(unique_labels) == len(allowed_provided_labels), "Redundant labels"
        self.allowed_provided_labels: Set[str] = unique_labels
        self.allowed_labels: Set[str] = unique_labels | {TO_REJECT_LABEL, TO_SKIP_LABEL}

    @property
    def n_products(self):
        return self.root.n_products

    @property
    def n_categories(self):
        return self.root.n_categories

    def get_category(self, category_id: int):
        return self._categories_by_id[int(category_id)]

    def get_product(self, product_id: int):
        return self._products_by_id[int(product_id)]

    def init_manual_labels(self, path: str):
        assert path is not None
        assert os.path.exists(path)
        path = os.path.abspath(path)

        if os.path.isdir(path):
            paths = glob.glob(os.path.join(path, "*.tsv"))
            if not paths:
                self._start_labelling(path)
            else:
                path = max(paths, key=os.path.getctime)
                self.load_manual_labels(path)

    def load_manual_labels(self, path: str):

        missing = 0
        selected = 0
        ambiguous = 0
        with open(path) as f:
            rows = csv.DictReader(f, delimiter="\t")
            labels = {}
            for row in rows:
                selected += 1
                product_id = row["product_id"]
                label = row["label"].strip()
                if not label:
                    missing += 1
                    continue
                label = label.split("|")
                if len(label) > 1:
                    ambiguous += 1
                    continue
                labels[product_id] = next(iter(label))

        logging.info(f"Loaded manual labels from {path}.")

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
        dir, _, content_hash, start, iteration = self.parse_path(path)
        assert (
            self.content_hash == content_hash
        ), "Different Frisco products dump was used"
        self.set_manual_labels(dir, start, iteration, labels)

    def set_manual_labels(
        self, dir: str, start: datetime, iteration: int, labels: Dict[ProductId, Label]
    ):
        self.labelling_dir = dir
        self.labelling_start = start
        self.labelling_iteration = (
            iteration + 1
        )  # Let's prepare for the next iteration...

        for product_id, label in labels.items():
            if self.allowed_labels:
                assert (
                    label in self.allowed_labels
                ), f"Unknown label {label}, expected one of: {self.allowed_labels}"
            product = self.get_product(product_id)
            product.labels.manual = label

    def try_save_labels_to_verify(self, path: Optional[str] = None) -> Optional[str]:

        if self.n_selected_for_verification_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                self.labelling_dir,
                self.content_hash,
                self.labelling_start,
                self.labelling_iteration,
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
                for product in self.root.products
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
                self.labelling_dir,
                self.content_hash,
                self.labelling_start,
                self.labelling_iteration,
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
            for product in self.root.products:
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

    @staticmethod
    def parse_path(path: str):
        root_dir = os.path.dirname(path)
        fname = os.path.basename(path)
        m = re.match(
            r"(?P<contenthash>[a-f0-9]{32})-(?P<startime>\d+)-(?P<iteration>\d+)-(to-verify|good-labels).tsv",
            fname,
        )
        assert m is not None
        path_parts = m.groupdict()
        content_hash = path_parts["contenthash"]
        starttime = datetime.strptime(path_parts["startime"], START_TIME_FORMAT)
        iteration = int(path_parts["iteration"])
        return root_dir, fname, content_hash, starttime, iteration

    @staticmethod
    def to_path(
        root_dir: str,
        content_hash: str,
        starttime: datetime,
        iteration: int,
        suffix: str,
        extension: str,
    ):
        fname = f"{content_hash}-{starttime.strftime(START_TIME_FORMAT)}-{iteration}-{suffix}.{extension}"
        return os.path.join(root_dir, fname)

    def _start_labelling(self, labelling_dir: str):
        self.labelling_start = datetime.now()
        self.labelling_iteration = 1
        self.labelling_dir = labelling_dir

    @property
    def shop_stats(self):
        n_categories_per_depth = Counter(
            category.depth for category in self.root.categories
        )
        n_categories_per_depth = {
            depth: n_categories
            for depth, n_categories in n_categories_per_depth.most_common()
        }
        return {
            "n_products": self.root.n_products,
            "n_categories": self.root.n_categories,
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
            for product in self.root.products
            if product.labels.manual and product.labels.manual in self.allowed_labels
        )

    @property
    def allowed_provided_labels_used(self):
        return set(
            product.labels.manual
            for product in self.root.products
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
            for product in self.root.products
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
            for product in self.root.products
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
            for product in self.root.products
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
                    for product in self.root.products
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
            for product in self.root.products
            if product.labels.selected and product.labels.is_ambiguous
        )

    @property
    def n_selected_for_verification_missing_labels(self):
        return sum(
            1
            for product in self.root.products
            if product.labels.selected and product.labels.is_missing
        )

    @property
    def n_selected_for_verification_labels(self):
        return sum(1 for product in self.root.products if product.labels.selected)

    @property
    def n_requires_verification_ambiguous_labels(self):
        return sum(
            1
            for product in self.root.products
            if product.labels.requires_verification() and product.labels.is_ambiguous
        )

    @property
    def n_required_verification_missing_labels(self):
        return sum(
            1
            for product in self.root.products
            if product.labels.requires_verification() and product.labels.is_missing
        )

    @property
    def n_requires_verification_labels(self):
        return sum(
            1
            for product in self.root.products
            if product.labels.requires_verification()
        )

    @property
    def n_ambiguous_labels(self):
        return sum(1 for product in self.root.products if product.labels.is_ambiguous)

    @property
    def n_missing_labels(self):
        return sum(1 for product in self.root.products if product.labels.is_missing)

    @property
    def n_to_reject_labels(self):
        return sum(1 for product in self.root.products if product.labels.to_reject)

    @property
    def n_to_skip_labels(self):
        return sum(1 for product in self.root.products if product.labels.to_skip)

    @property
    def n_good_labels(self):
        return sum(1 for product in self.root.products if product.labels.is_good)

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
        return sum(1 for product in self.root.products if product.labels.manual)

    def save_stats(self, path: Optional[str] = None):
        if path is None:
            path = self.to_path(
                self.labelling_dir,
                self.content_hash,
                self.labelling_start,
                self.labelling_iteration,
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
            "start_time": self.labelling_start.isoformat(),
            "iteration": self.labelling_iteration,
            "stats": self.stats,
        }
        encoder = CustomEncoder()
        with jsonlines.open(path, "a", dumps=encoder.encode) as writer:
            writer.write(iteration_stats)
        logging.info(f"Updated all iterations stats in {path}.")

    @property
    def all_stats_path(self):
        return self.to_path(
            self.labelling_dir,
            self.content_hash,
            self.labelling_start,
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
