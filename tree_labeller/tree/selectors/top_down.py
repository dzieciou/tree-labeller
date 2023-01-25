from collections import defaultdict
from itertools import zip_longest
import random

from anytree import NodeMixin, LevelOrderGroupIter, PreOrderIter, SymlinkNode


def select_top_down(tree: NodeMixin, k: int):
    categories_only = view_without_leaves(tree)
    assert len(categories_only.leaves) >= k

    selected_categories = set()
    for category in iterate(categories_only):
        if category.parent != None:
            selected_categories.discard(category.parent)
        selected_categories.add(category)
        if len(selected_categories) == k:
            break

    # Some categories might be non leaf
    selected_categories = (
        random.choice(category.leaves) for category in selected_categories
    )

    # back from view to original tree
    selected_categories = (category.target for category in selected_categories)
    selected_products = set()
    for category in selected_categories:
        product = random.choice(category.children)
        selected_products.add(product)
    return selected_products


def iterate(tree: NodeMixin):
    for children in LevelOrderGroupIter(tree):
        children_per_parent = defaultdict(set)
        for child in children:
            children_per_parent[child.parent].add(child)
        for selected in zip_longest(*children_per_parent.values()):
            yield from (node for node in selected if node != None)


def view_without_leaves(tree: NodeMixin):
    mapping = {}
    for node in PreOrderIter(tree):
        if node.is_leaf:  # Product, while we only want Categories/Inner Nodes
            continue
        mapped_parent = None if node.is_root else mapping[node.parent]
        mapped_node = SymlinkNode(target=node, parent=mapped_parent)
        mapping[node] = mapped_node

    return mapping[tree]
