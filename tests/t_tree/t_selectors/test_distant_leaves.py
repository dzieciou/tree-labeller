from anytree import AnyNode, RenderTree, ContRoundStyle

from tree_labeller.tree.selectors.distant_leaves import (
    _to_binary_tree,
    select_distant_leaves,
    _select_distant_leaves_binary_tree,
)


def test_to_binary_tree():
    # TODO Turn into a test, add assertions

    v = AnyNode(id="v")
    v1 = AnyNode(v, id="v1")
    v2 = AnyNode(v, id="v2")
    v3 = AnyNode(v, id="v3")
    v11 = AnyNode(v1, id="v11")
    v12 = AnyNode(v1, id="v12")
    v13 = AnyNode(v1, id="v13")
    v31 = AnyNode(v3, id="v31")

    print(RenderTree(v, style=ContRoundStyle()))
    print()
    binary_tree = _to_binary_tree(v)
    print(RenderTree(binary_tree, style=ContRoundStyle()))


def test_select_distant_leaves():

    v = AnyNode(id="v")
    v1 = AnyNode(v, id="v1")
    v2 = AnyNode(v, id="v2")
    v3 = AnyNode(v, id="v3")
    v11 = AnyNode(v1, id="v11")
    v12 = AnyNode(v1, id="v12")
    v13 = AnyNode(v1, id="v13")
    print(RenderTree(v, style=ContRoundStyle()))
    print()

    leaves, total_distance = select_distant_leaves(v, 3)
    # assert total_distance == 500
    assert leaves == {v2, v3, v11} or leaves == {v2, v3, v12} or leaves == {v2, v3, v13}


def test_select_distant_leaves_2():

    v = AnyNode(id="v")
    v1 = AnyNode(v, id="v1")
    v2 = AnyNode(v, id="v2")
    v3 = AnyNode(v, id="v3")
    v11 = AnyNode(v1, id="v11")
    v12 = AnyNode(v1, id="v12")
    v13 = AnyNode(v1, id="v13")
    v111 = AnyNode(v11, id="v111")
    v112 = AnyNode(v11, id="v112")
    v113 = AnyNode(v11, id="v113")

    print(RenderTree(v, style=ContRoundStyle()))
    print()

    leaves = select_distant_leaves(v, 3)
    assert leaves == {v2, v3, v113}


def test_select_distant_leaves_binary_tree_1():

    v = AnyNode(id="v")
    v1 = AnyNode(parent=v, id="v1")
    v2 = AnyNode(parent=v, id="v2")
    v11 = AnyNode(parent=v1, id="v11")
    v12 = AnyNode(parent=v1, id="v12")
    print(RenderTree(v, style=ContRoundStyle()))
    print()

    leaves = _select_distant_leaves_binary_tree(v, 1)
    assert leaves == {v2} or leaves == {v11} or leaves == {v12}


def test_select_distant_leaves_binary_tree_2():

    v = AnyNode(id="v")
    v1 = AnyNode(parent=v, id="v1")
    v2 = AnyNode(parent=v, id="v2")
    v11 = AnyNode(parent=v1, id="v11")
    v12 = AnyNode(parent=v1, id="v12")

    print(RenderTree(v, style=ContRoundStyle()))
    print()

    leaves = _select_distant_leaves_binary_tree(v, 2)
    assert leaves == {v2, v12} or leaves == {v2, v11}
