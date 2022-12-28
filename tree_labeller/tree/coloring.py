from typing import TypeVar, Set

from anytree import NodeMixin, SymlinkNode, PreOrderIter

from tree_labeller.tree.utils import internals

Color = TypeVar("Color")


class ColorableNode(NodeMixin):
    def __init__(
        self,
        target=None,
        parent=None,
        colors: Set[Color] = None,
    ):
        self.target = target
        self.parent = parent
        self.colors = colors if colors is not None else set()

    def add_color(self, color: Color):
        self.colors.add(color)

    def is_multicolor(self):
        return len(self.colors) > 1

    def is_colorless(self):
        return len(self.colors) == 0

    def requires_verification(self):
        return self.is_colorless() or self.is_multicolor()


def color_tree(root: NodeMixin):
    """
    Given a tree with some leaves colored, the goal is to color remaining nodes the tree.

    The rules are:
    - an internal node can be colored with one or more colors
    - if an internal node has at least descending leaf colored, then it should be colored only with colors of its leaves
    - otherwise, it should be colored with colors of leaves of its siblings

    The algorithm is roughly based on.
    https://cs.stackexchange.com/questions/134042/finding-largest-disjoint-subtrees-spanning-nodes
    """

    assert all(internal.is_colorless() for internal in internals(root))
    assert any(leaf.colors for leaf in root.leaves)
    assert not any(leaf.is_multicolor() for leaf in root.leaves)

    def color_from_children(node: ColorableNode):
        if not node.parent:
            return
        node.parent.colors.update(node.colors)
        color_from_children(node.parent)

    def color_from_parent(node: ColorableNode):
        # TODO Maybe too much recurrence for deep and breadth trees
        for child in node.children:
            if not child.colors:
                child.colors = node.colors
            color_from_parent(child)

    for leaf in root.leaves:
        if leaf.colors:
            color_from_children(leaf)

    color_from_parent(root)


def select_subtree_requiring_verification(root: ColorableNode) -> SymlinkNode:

    mapping = {}

    def create_link(node: NodeMixin, new_parent: SymlinkNode = None):
        link = SymlinkNode(target=node, parent=new_parent)
        mapping[node] = link
        return link

    for node in PreOrderIter(root):
        if node.is_multicolor() or node.is_colorless():
            new_parent = mapping.get(node.parent)
            create_link(node, new_parent)

    return mapping.get(root)
