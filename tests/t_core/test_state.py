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
