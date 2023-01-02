import csv

import pytest

from tree_labeller.core.state import LabelingState
from tree_labeller.core.types import LabelableCategory, LabelableProduct


def test_save_to_verify(tmp_path):
    # given
    tree = LabelableCategory(id=0, name="categories")
    category1 = LabelableCategory(id=1, name="category1", parent=tree)
    product1 = LabelableProduct(
        id=1, name="product1", brand="brand1", category=category1
    )
    product1.labels.selected = True
    product1.labels.predicted = ["Z", "Y", "X"]
    product2 = LabelableProduct(
        id=2, name="product2", brand="brand1", category=category1
    )
    product2.labels.selected = True
    product2.labels.manual = "Y"
    product3 = LabelableProduct(
        id=3, name="product3", brand="brand1", category=category1
    )
    product3.labels.selected = False
    product3.labels.predicted = ["Z", "Y", "X"]
    state = LabelingState(tree, iteration=1)

    # when
    path = tmp_path / "state.tsv"
    state.save_to_verify(path)

    # then
    with open(path) as f:
        rows = csv.DictReader(f, delimiter="\t")
        rows = list(rows)
    assert rows == [
        {
            "id": "1",
            "name": "product1",
            "brand": "brand1",
            "category": "categories>category1",
            "label": "X|Y|Z",
        },
        {
            "brand": "brand1",
            "category": "categories>category1",
            "id": "2",
            "label": "Y",
            "name": "product2",
        },
    ]


def test_save_good_predicted_labels(tmp_path):
    # given
    tree = LabelableCategory(id=0, name="categories")
    category1 = LabelableCategory(id=1, name="category1", parent=tree)
    product1 = LabelableProduct(
        id=1, name="product1", brand="brand1", category=category1
    )
    product1.labels.predicted = ["Z", "Y", "X"]
    product2 = LabelableProduct(
        id=2, name="product2", brand="brand1", category=category1
    )
    product2.labels.predicted = ["Y"]
    product3 = LabelableProduct(
        id=3, name="product3", brand="brand1", category=category1
    )
    product3.labels.predicted = None
    state = LabelingState(tree, iteration=1)

    # when
    path = tmp_path / "state.tsv"
    state.save_good_predicted_labels(path)

    # then
    with open(path) as f:
        rows = csv.DictReader(f, delimiter="\t")
        rows = list(rows)
    assert rows == [
        {
            "brand": "brand1",
            "category": "categories>category1",
            "id": "2",
            "label": "Y",
            "name": "product2",
        },
    ]


def test_to_mapping():
    tree = LabelableCategory(id=0, name="categories")
    tree.labels.predicted = {"A", "B"}
    category1 = LabelableCategory(id=1, name="category1", parent=tree)
    category1.labels.predicted = {"B"}
    category11 = LabelableCategory(id=11, name="category11", parent=category1)
    category11.labels.predicted = {"B"}
    category12 = LabelableCategory(id=12, name="category12", parent=category1)
    category12.labels.predicted = {"B"}
    category2 = LabelableCategory(id=2, name="category2", parent=tree)
    category2.labels.predicted = {"A"}
    category3 = LabelableCategory(id=3, name="category3", parent=tree)
    category3.labels.predicted = {"A"}

    state = LabelingState(tree, iteration=1)
    mapping = state.to_mapping()
    assert mapping == [
        {"id": 2, "category": "categories>category2", "label": "A"},
        {"id": 3, "category": "categories>category3", "label": "A"},
        {"id": 1, "category": "categories>category1", "label": "B"},
    ]


def test_from_dir():
    # TODO: Test
    pass
