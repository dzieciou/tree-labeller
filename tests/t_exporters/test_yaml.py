import textwrap

from tree_labeller.core.types import Category, Product

import pytest

from tree_labeller.exporters.yaml import export_tree


def test_export_tree(tmp_path):
    expected_doc = """\
    name: categories
    id: 1
    children:
    - name: Alcoholic Drinks
      id: 11
      children:
      - name: Whiskies
        id: 111
        children:
        - name: Jack Daniel's
          id: 1111
        - name: Johnnie Walker's
          id: 1112
        """

    tree = Category("categories", id=1)
    c11 = Category("Alcoholic Drinks", id=11, parent=tree)
    c111 = Category("Whiskies", id=111, parent=c11)
    Product("Jack Daniel's", id=1111, category=c111)
    Product("Johnnie Walker's", id=1112, category=c111)
    path = tmp_path / "tree.yaml"
    export_tree(tree, str(path))
    with open(path) as f:
        doc = f.read()
    assert textwrap.dedent(doc) == textwrap.dedent(expected_doc)
