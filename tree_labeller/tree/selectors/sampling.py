"""
Sample products from a tree

We first sample leaf-categories without repetition.

Then, for each sampled category one product is sampled.

This is based on the assumption that products with the same leaf-category will be labelled with the same label (which, obviously might be not true)


"""

import random

from anytree import NodeMixin, LevelOrderGroupIter, PreOrderIter, SymlinkNode

# To support reproducibility
random.seed(42)


def sample(tree: NodeMixin, k: int):
    categories_only = view_without_leaves(tree)
    calc_prob(categories_only)
    population = categories_only.leaves
    weights = [leaf.prob for leaf in population]

    k = min(len(weights), k)
    sampled_categories = weighted_sample_without_replacement(population, weights, k)
    sampled_categories = (category.target for category in sampled_categories)
    sampled_products = set()
    for category in sampled_categories:
        product = random.choice(category.children)
        sampled_products.add(product)
    return sampled_products


def view_without_leaves(tree: NodeMixin):
    mapping = {}
    for node in PreOrderIter(tree):
        if node.is_leaf:  # Product, while we only want Categories/Inner Nodes
            continue
        mapped_parent = None if node.is_root else mapping[node.parent]
        mapped_node = SymlinkNode(target=node, parent=mapped_parent)
        mapping[node] = mapped_node

    return mapping[tree]


def calc_prob(tree: NodeMixin):
    tree.prob = 1.0
    for children in LevelOrderGroupIter(tree):
        prob = 1.0 / len(children)
        for child in children:
            if not child.is_root:
                child.prob = child.parent.prob * prob


def weighted_sample_without_replacement(population, weights, k=1):
    assert len(population) == len(weights)
    assert k >= len(population)

    weights = list(weights)
    positions = range(len(population))
    indices = []
    while True:
        needed = k - len(indices)
        if not needed:
            break
        for i in random.choices(positions, weights, k=needed):
            if weights[i]:
                weights[i] = 0.0
                indices.append(i)
    return [population[i] for i in indices]
