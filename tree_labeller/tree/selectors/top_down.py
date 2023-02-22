"""
Selects a subset of k leaves from a tree, following a top-down approach.

Let's call leaves -- products and inner nodes -- categories.

The idea is to sample products from as many root categories as your budget k permits.

If the budget permits choosing more than one product from a root category, then subcategories from root categories are selected, and so on.

Subcategories are selected in a specific way. For each root category, 1st subcategory is selected, then 2nd subcategory, and so on as long as there is still a budget. This way selected subcategories will represent as many root categories as the budget permits.

Finally, for each selected category a random product is drawn.
"""

import random
from collections import defaultdict
from itertools import zip_longest
from typing import Set, Generator

from anytree import NodeMixin, LevelOrderGroupIter, PreOrderIter, SymlinkNode


def select_top_down(tree: NodeMixin, k: int) -> Set[NodeMixin]:
    categories_only = _view_without_leaves(tree)
    selected_categories = _select_categories(categories_only, k)
    selected_categories = {c.target for c in selected_categories}
    return _select_products(selected_categories)


def _select_products(categories: Set[NodeMixin]) -> Set[NodeMixin]:
    selected_products = set()
    for category in categories:
        product = random.choice(category.leaves)
        selected_products.add(product)
    return selected_products


def _select_categories(tree: NodeMixin, k: int) -> Set[NodeMixin]:
    assert len(tree.leaves) >= k
    selected_categories = set()
    for category in _iterate(tree):
        selected_categories.discard(category.parent)
        selected_categories.add(category)
        if len(selected_categories) == k:
            break
    return selected_categories


def _iterate(tree: NodeMixin, shuffle: bool = True) -> Generator[NodeMixin, None, None]:
    for children in LevelOrderGroupIter(tree):
        if shuffle:
            children = list(children)
            random.shuffle(children)
        children_per_parent = defaultdict(list)
        for child in children:
            children_per_parent[child.parent].append(child)
        for selected in zip_longest(*children_per_parent.values()):
            yield from (node for node in selected if node != None)


def _view_without_leaves(tree: NodeMixin) -> SymlinkNode:
    mapping = {}
    for node in PreOrderIter(tree):
        if node.is_leaf:  # Product, while we only want Categories/Inner Nodes
            continue
        mapped_parent = None if node.is_root else mapping[node.parent]
        mapped_node = SymlinkNode(target=node, parent=mapped_parent)
        mapping[node] = mapped_node

    return mapping[tree]
