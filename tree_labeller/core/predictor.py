from anytree import PreOrderIter

from tree_labeller.core.types import Category, Product
from tree_labeller.tree.coloring import (
    ColorableNode,
    color_tree,
    select_subtree_requiring_verification,
)
from tree_labeller.tree.distant_leaves import find_distant_leaves
from tree_labeller.tree.utils import internals


def _to_colorable_tree(tree):
    mapping = {}
    for node in PreOrderIter(tree):
        if node.labels.to_skip:
            continue
        new_parent = mapping.get(node.parent)
        new_node = ColorableNode(
            node,
            parent=new_parent,
            colors={node.labels.manual} if node.labels.manual else set(),
        )
        mapping[node] = new_node
    return mapping[tree]


def predict(tree: Category, n_sample: int):
    assert all(isinstance(leaf, Product) for leaf in tree.leaves)
    assert all(isinstance(internal, Category) for internal in internals(tree))
    assert all(node.labels.predicted is None for node in PreOrderIter(tree))
    assert all(category.labels.manual is None for category in internals(tree))

    colorable_tree = _to_colorable_tree(tree)
    if any(leaf.labels.manual for leaf in tree.leaves):
        color_tree(colorable_tree)
        for node in PreOrderIter(colorable_tree):
            node.target.labels.predicted = node.colors

        good_leaves = [leaf for leaf in colorable_tree.leaves if len(leaf.colors) == 1]
        for leaf in good_leaves:
            leaf.target.labels.predicted = leaf.colors

    requires_verification = select_subtree_requiring_verification(colorable_tree)
    if requires_verification:
        sampled_requires_verification, _ = find_distant_leaves(
            requires_verification, n_sample
        )
        sampled_requires_verification = [
            node.target for node in sampled_requires_verification
        ]
        for leaf in sampled_requires_verification:
            leaf.target.labels.selected = True
