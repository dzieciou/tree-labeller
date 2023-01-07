import csv
import itertools
import logging
import os.path
import shutil
from collections import Counter
from datetime import datetime
from typing import Iterable, Set, Optional, List, Callable

import yaml

from tree_labeller.core import predictor
from tree_labeller.core.state import LabelingState
from tree_labeller.core.types import (
    TO_REJECT_LABEL,
    TO_SKIP_LABEL,
    Label,
    LabelableCategory,
    LabelableProduct,
)

CONFIGURATION_FILE = "config.yaml"

START_TIME_FORMAT = "%Y%m%d%H%M%S"


class Config:
    dir: str
    tree_path: str
    original_tree_path: str
    allowed_provided_labels: Set[str]
    start_time: datetime

    def __init__(
        self,
        dir: str,
        tree_path: str,
        original_tree_path: str,
        allowed_labels: Set[str],
        start_time: Optional[datetime] = None,
    ):
        assert os.path.isdir(dir)

        unique_labels = set(allowed_labels)
        assert len(unique_labels) == len(
            allowed_labels
        ), f"Redundant labels in: {allowed_labels}"

        self.dir = dir
        self.tree_path = tree_path
        self.original_tree_path = original_tree_path
        self.allowed_provided_labels = set(allowed_labels)
        self.start_time: datetime = start_time or datetime.now()

    @classmethod
    def from_yaml(cls, path: str):
        with open(path) as f:
            config = yaml.safe_load(f)
        return cls(**config)

    def to_yaml(self, path: str):
        config = {
            "dir": self.dir,
            "tree_path": self.tree_path,
            "original_tree_path": self.original_tree_path,
            "allowed_labels": list(self.allowed_provided_labels),
            "start_time": self.start_time,
        }
        with open(path, "w") as out:
            yaml.dump(config, out)


class LabellingTask:
    @classmethod
    def initialize(
        cls, dir: str, tree_path: str, allowed_provided_labels: Set[Label]
    ) -> "LabellingTask":
        dir = os.path.abspath(dir)
        try:
            os.makedirs(dir, exist_ok=False)
        except FileExistsError:
            print(f"Directory {dir} already exists. Perhaps this is a previous task?")
            return

        tree_path = os.path.abspath(tree_path)
        dest_tree_path = os.path.join(dir, os.path.basename(tree_path))
        shutil.copy(tree_path, dest_tree_path)

        config = Config(
            dir=dir,
            tree_path=dest_tree_path,
            original_tree_path=tree_path,
            allowed_labels=allowed_provided_labels,
        )
        config.to_yaml(os.path.join(dir, CONFIGURATION_FILE))
        logging.info(f"Created task in: {dir}")

        return cls.from_dir(dir)

    @classmethod
    def from_dir(cls, dir: str) -> "LabellingTask":
        dir = os.path.abspath(dir)
        config = Config.from_yaml(os.path.join(dir, CONFIGURATION_FILE))
        allowed_labels = config.allowed_provided_labels | {
            TO_REJECT_LABEL,
            TO_SKIP_LABEL,
        }
        state = LabelingState.from_dir(dir, config.tree_path, allowed_labels)
        task = LabellingTask(dir, config, state, allowed_labels)
        return task

    def __init__(
        self,
        dir: str,
        config: Config,
        state: LabelingState,
        allowed_labels: Set[Label],
    ):

        assert dir != None
        assert config != None
        assert state != None

        self.dir = os.path.abspath(dir)
        self.config = config
        self.state = state
        self.allowed_labels = allowed_labels
        self.predictor: Callable[[LabelableCategory, int], None] = predictor.predict

    @property
    def n_products(self):
        return self.state.tree.n_products

    @property
    def n_categories(self):
        return self.state.tree.n_categories

    def try_save_labels_to_verify(self, path: Optional[str] = None) -> Optional[str]:

        if self.n_selected_for_verification_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                "to-verify",
                "tsv",
            )

        self.state.save_to_verify(path)

        return path

    def try_save_good_predicted_labels(
        self, path: Optional[str] = None
    ) -> Optional[str]:

        if self.n_good_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                "good",
                "tsv",
            )

        self.state.save_good_predicted_labels(path)

        return path

    def try_save_mapping(self, path: Optional[str] = None) -> Optional[str]:

        if self.n_good_labels == 0:
            return None

        if path is None:
            path = self.to_path(
                "mapping",
                "tsv",
            )

        self.state.save_mapping(path)

        return path

    def to_path(
        self,
        suffix: str,
        extension: str,
    ):
        fname = f"{self.state.iteration}-{suffix}.{extension}"
        return os.path.join(self.dir, fname)

    @property
    def tree_stats(self):
        n_categories_per_depth = Counter(
            category.depth for category in self.state.tree.categories
        )
        n_categories_per_depth = {
            depth: n_categories
            for depth, n_categories in n_categories_per_depth.most_common()
        }
        return {
            "n_products": self.state.tree.n_products,
            "n_categories": self.state.tree.n_categories,
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
            for product in self.state.tree.products
            if product.labels.manual and product.labels.manual in self.allowed_labels
        )

    @property
    def allowed_provided_labels_used(self):
        return set(
            product.labels.manual
            for product in self.state.tree.products
            if product.labels.manual
            and product.labels.manual in self.config.allowed_provided_labels
        )

    @property
    def allowed_labels_not_used(self) -> Set[str]:
        return self.allowed_labels - self.allowed_labels_used

    @property
    def allowed_provided_labels_not_used(self) -> Set[str]:
        return self.config.allowed_provided_labels - self.allowed_provided_labels_used

    @property
    def n_allowed_labels(self):
        return len(self.allowed_labels) if self.allowed_labels else None

    @property
    def n_allowed_provided_labels(self):
        return (
            len(self.config.allowed_provided_labels)
            if self.config.allowed_provided_labels
            else None
        )

    @property
    def n_products_per_manual_label(self):
        n_products_per_manual_label = Counter(
            product.labels.manual
            for product in self.state.tree.products
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
            for product in self.state.tree.products
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
            for product in self.state.tree.products
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
                    for product in self.state.tree.products
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
            for product in self.state.tree.products
            if product.labels.selected and product.labels.is_ambiguous
        )

    @property
    def n_selected_for_verification_missing_labels(self):
        return sum(
            1
            for product in self.state.tree.products
            if product.labels.selected and product.labels.is_missing
        )

    @property
    def n_selected_for_verification_labels(self):
        return sum(1 for product in self.state.tree.products if product.labels.selected)

    @property
    def n_requires_verification_ambiguous_labels(self):
        return sum(
            1
            for product in self.state.tree.products
            if product.labels.requires_verification() and product.labels.is_ambiguous
        )

    @property
    def n_required_verification_missing_labels(self):
        return sum(
            1
            for product in self.state.tree.products
            if product.labels.requires_verification() and product.labels.is_missing
        )

    @property
    def n_requires_verification_labels(self):
        return sum(
            1
            for product in self.state.tree.products
            if product.labels.requires_verification()
        )

    @property
    def n_ambiguous_labels(self):
        return sum(
            1 for product in self.state.tree.products if product.labels.is_ambiguous
        )

    @property
    def n_missing_labels(self):
        return sum(
            1 for product in self.state.tree.products if product.labels.is_missing
        )

    @property
    def n_to_reject_labels(self):
        return sum(
            1 for product in self.state.tree.products if product.labels.to_reject
        )

    @property
    def n_to_skip_labels(self):
        return sum(1 for product in self.state.tree.products if product.labels.to_skip)

    @property
    def n_good_labels(self):
        return sum(1 for product in self.state.tree.products if product.labels.is_good)

    @property
    def iteration_stats(self):
        return {
            "tree": self.tree_stats,
            "manual_labels": self.manual_labels_stats,
            "predicted_labels": self.predicted_labels_stats,
            "progress.py": self.progress,
        }

    @property
    def n_manual_labels(self):
        return sum(1 for product in self.state.tree.products if product.labels.manual)

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

    def predict_labels(self, n_sample: int):
        self.predictor(self.state.tree, n_sample)
        self.state.iteration += 1


def save_products(products: Iterable[LabelableProduct], path: str):
    products = sorted(products, key=lambda product: product.category_name)
    with open(path, "w") as f:
        writer = csv.DictWriter(
            f, fieldnames=LabelableProduct.fieldnames, delimiter="\t"
        )
        writer.writeheader()
        for product in products:
            writer.writerow(product.asdict())


def load_allowed_labels(path: str) -> List[str]:
    with open(path) as f:
        labels = [label.strip() for label in f.readlines()]
    return labels
