from typing import Set

from anytree import PreOrderIter, NodeMixin

from tree_labeller.core.types import LabelableCategory, LabelableProduct, Label
from tree_labeller.tree.coloring import (
    ColorableNode,
    color_tree,
    select_subtree_requiring_verification,
)
from tree_labeller.tree.selectors import select_top_down
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


sampler = select_top_down  # select_distant_leaves


def predict(tree: LabelableCategory, allowed_labels: Set[Label]):
    assert all(isinstance(leaf, LabelableProduct) for leaf in tree.leaves)
    assert all(isinstance(internal, LabelableCategory) for internal in internals(tree))
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
        sample_size = get_sample_size(requires_verification, allowed_labels)
        sampled_requires_verification = sampler(requires_verification, sample_size)
        sampled_requires_verification = [
            node.target.target for node in sampled_requires_verification
        ]
        for leaf in sampled_requires_verification:
            leaf.labels.selected = True


def get_sample_size(tree: NodeMixin, allowed_labels: Set[Label]):
    return max(len(allowed_labels), len(tree.children))
