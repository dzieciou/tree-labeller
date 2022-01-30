from anytree import PreOrderIter

from labeller.shop import Product, Shop, Category
from labeller.tree.coloring import (
    ColoredNode,
    color_tree,
    select_subtree_requiring_verification,
)
from labeller.tree.distant_leaves import find_distant_leaves
from labeller.tree.utils import internals


def predict_labels(shop: Shop, n_sample: int):
    root = shop.root
    assert all(isinstance(leaf, Product) for leaf in root.leaves)
    assert all(isinstance(internal, Category) for internal in internals(root))
    assert all(node.labels.predicted is None for node in PreOrderIter(shop.root))
    assert all(category.labels.manual is None for category in internals(shop.root))

    colored_root = to_colored_tree(root)
    if any(leaf.labels.manual for leaf in root.leaves):
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


def to_colored_tree(root):
    mapping = {}
    for node in PreOrderIter(root):
        if node.labels.to_skip:
            continue
        new_parent = mapping.get(node.parent)
        new_node = ColoredNode(
            node,
            parent=new_parent,
            colors={node.labels.manual} if node.labels.manual else set(),
        )
        mapping[node] = new_node
    return mapping[root]
