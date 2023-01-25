from anytree import Node, AsciiStyle, RenderTree

from tree_labeller.tree.selectors.top_down import iterate


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
    l = [l.name for l in iterate(f, shuffle=False)]
    assert l == ["f", "b", "g", "a", "i", "d", "h", "c", "e"]
