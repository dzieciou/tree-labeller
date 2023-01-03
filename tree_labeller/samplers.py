import random
from collections import Counter

from anytree import NodeMixin


def sample(tree: NodeMixin, k: int):
    if tree.is_leaf:
        yield tree
        return
    children = list(tree.children)
    leaves_by_child = [len(child.leaves) for child in children]
    samples = random.choices(children, weights=leaves_by_child, k=k)
    child_counts = Counter(samples)
    for child, count in child_counts:
        sample(child, k=count)