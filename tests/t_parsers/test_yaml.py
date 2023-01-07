from anytree import PreOrderIter, NodeMixin

from tree_labeller.core.types import LabelableCategory, LabelableProduct
from tree_labeller.parsers.yaml import YamlTreeParser

import pytest


def test_parse(tmp_path):
    yaml_doc = """
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
    path = tmp_path / "doc.yaml"
    with open(path, "w") as f:
        f.write(yaml_doc)

    expected_tree = LabelableCategory("categories", id=1)
    c11 = LabelableCategory("Alcoholic Drinks", id=11, parent=expected_tree)
    c111 = LabelableCategory("Whiskies", id=111, parent=c11)
    LabelableProduct("Jack Daniel's", id=1111, category=c111)
    LabelableProduct("Johnnie Walker's", id=1112, category=c111)

    tree = YamlTreeParser().parse_tree(path)
    assert_tree_equality(tree, expected_tree)


def assert_tree_equality(t1: NodeMixin, t2: NodeMixin):
    for n1, n2 in zip(PreOrderIter(t1), PreOrderIter(t2)):
        assert type(n1) == type(n2)
        assert n1 == n2
