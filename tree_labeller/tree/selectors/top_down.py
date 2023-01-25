import random
from collections import defaultdict
from itertools import zip_longest

from anytree import NodeMixin, LevelOrderGroupIter, PreOrderIter, SymlinkNode

random.seed(42)

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

    # back from view to original tree
    selected_categories = (category.target for category in selected_categories)
    selected_products = set()
    for category in selected_categories:
        product = random.choice(category.leaves)
        selected_products.add(product)
    return selected_products


def iterate(tree: NodeMixin):
    for children in LevelOrderGroupIter(tree):
        children = list(children)
        random.shuffle(children)
        children_per_parent = defaultdict(list)
        for child in children:
            children_per_parent[child.parent].append(child)
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
