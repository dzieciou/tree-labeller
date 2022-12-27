from anytree import PreOrderIter

from labeller.task import LabellingTask
from labeller.types import Category, Product
from labeller.tree.coloring import (
    ColoredNode,
    color_tree,
    select_subtree_requiring_verification,
)
from labeller.tree.distant_leaves import find_distant_leaves
from labeller.tree.utils import internals


def predict_labels(task: LabellingTask, n_sample: int):
    tree = task.state.tree

    assert all(isinstance(leaf, Product) for leaf in tree.leaves)
    assert all(isinstance(internal, Category) for internal in internals(tree))
    assert all(node.labels.predicted is None for node in PreOrderIter(tree))
    assert all(category.labels.manual is None for category in internals(tree))



    colored_root = to_colored_tree(tree)
    if any(leaf.labels.manual for leaf in tree.leaves):
        color_tree(colored_root)
        for node in PreOrderIter(colored_root):
            node.target.labels.predicted = node.colors

        good_leaves = [leaf for leaf in colored_root.leaves if len(leaf.colors) == 1]
        for leaf in good_leaves:
            leaf.target.labels.predicted = leaf.colors

    requires_verification = select_subtree_requiring_verification(colored_root)
    if requires_verification:
        sampled_requires_verification, _ = find_distant_leaves(
            requires_verification, n_sample
        )
        sampled_requires_verification = [
            node.target for node in sampled_requires_verification
        ]
        for leaf in sampled_requires_verification:
            leaf.target.labels.selected = True

    task.state.iteration += 1

def to_colored_tree(tree):
    mapping = {}
    for node in PreOrderIter(tree):
        if node.labels.to_skip:
            continue
        new_parent = mapping.get(node.parent)
        new_node = ColoredNode(
            node,
            parent=new_parent,
            colors={node.labels.manual} if node.labels.manual else set(),
        )
        mapping[node] = new_node
    return mapping[tree]
