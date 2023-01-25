import pytest
from anytree import Node, AsciiStyle, RenderTree

from tree_labeller.tree.selectors import top_down


def test_iterate():
    f = Node("f")
    b = Node("b", parent=f)
    a = Node("a", parent=b)
    d = Node("d", parent=b)
    c = Node("c", parent=b)
    g = Node("g", parent=f)
    i = Node("i", parent=g)
    h = Node("h", parent=g)
    e = Node("e", parent=h)

    print(RenderTree(f, style=AsciiStyle()).by_attr())
    nodes = [node.name for node in top_down._iterate(f, shuffle=False)]
    assert nodes == ["f", "b", "g", "a", "i", "d", "h", "c", "e"]


def test_select_categories():
    f = Node("f")
    b = Node("b", parent=f)
    c = Node("c", parent=b)
    g = Node("g", parent=f)
    i = Node("i", parent=g)
    h = Node("h", parent=g)
    e = Node("e", parent=h)
    print(RenderTree(f, style=AsciiStyle()).by_attr())

    nodes = [node.name for node in top_down._select_categories(f, k=1)]
    assert nodes == ["f"]

    nodes = {node.name for node in top_down._select_categories(f, k=2)}
    assert nodes == {"b", "g"}

    nodes = {node.name for node in top_down._select_categories(f, k=3)}
    assert nodes == {"h", "i", "c"}

    with pytest.raises(AssertionError):
        # Too many categories to select
        top_down._select_categories(f, k=4)
