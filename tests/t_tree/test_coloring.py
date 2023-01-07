from typing import Set

import pytest
from anytree import PreOrderIter

from tree_labeller.tree.coloring import (
    ColorableNode,
    select_subtree_requiring_verification,
    color_tree,
    Color,
)


class MockedColorableNode(ColorableNode):
    def __init__(
        self,
        parent=None,
        id: str = None,
        colors: Set[Color] = None,
    ):
        super().__init__(None, parent, colors)
        self.id = id


def test_coloring_1():
    v = MockedColorableNode(id="v")
    v1 = MockedColorableNode(v, id="v1")
    v2 = MockedColorableNode(v, id="v2", colors={"blue"})

    color_tree(v)

    assert v.colors == {"blue"}
    assert v1.colors == {"blue"}
    assert v2.colors == {"blue"}


def test_coloring_2():
    v = MockedColorableNode(id="v")
    v1 = MockedColorableNode(v, id="v1", colors={"green"})
    v2 = MockedColorableNode(v, id="v2", colors={"blue"})

    color_tree(v)

    assert v.colors == {"blue", "green"}
    assert v1.colors == {"green"}
    assert v2.colors == {"blue"}


def test_coloring_3():
    v = MockedColorableNode(id="v")
    v1 = MockedColorableNode(v, id="v1", colors={"green"})
    v2 = MockedColorableNode(v, id="v2", colors={"blue"})
    v3 = MockedColorableNode(v, id="v3")

    color_tree(v)

    assert v.colors == {"blue", "green"}
    assert v1.colors == {"green"}
    assert v2.colors == {"blue"}
    assert v3.colors == {"blue", "green"}


def test_coloring_internal_node_colored():
    v = MockedColorableNode(id="v", colors={"green"})
    v1 = MockedColorableNode(v, id="v1", colors={"green"})
    v2 = MockedColorableNode(v, id="v2", colors={"blue"})

    with pytest.raises(AssertionError) as ex:
        color_tree(v)


def test_coloring_no_leaf_colored():
    v = MockedColorableNode(id="v")
    v1 = MockedColorableNode(v, id="v1")
    v2 = MockedColorableNode(v, id="v2")

    with pytest.raises(AssertionError) as ex:
        color_tree(v)


def test_coloring_multi_colored_leaf():
    v = MockedColorableNode(id="v")
    v1 = MockedColorableNode(v, id="v1", colors={"blue", "green"})
    v2 = MockedColorableNode(v, id="v2")

    with pytest.raises(AssertionError) as ex:
        color_tree(v)


def test_select_subtree_requiring_verification_1():
    v = MockedColorableNode(id="v", colors={"green", "blue"})
    v1 = MockedColorableNode(v, id="v1", colors={"green"})
    v2 = MockedColorableNode(v, id="v2", colors={"blue"})
    v3 = MockedColorableNode(v, id="v3", colors={"green", "blue"})

    subtree = select_subtree_requiring_verification(v)
    nodes = [node.target for node in PreOrderIter(subtree)]
    assert nodes == [v, v3]
