import random
from collections import Counter

from anytree import NodeMixin


def sample(tree: NodeMixin, n: int):
    if tree.is_leaf:
        yield tree
        return
    children = list(tree.children)
    leaves_by_child = [
        min(len(child.children), len(child.leaves)) for child in children
    ]
    samples = random.choices(children, weights=leaves_by_child, k=n)
    child_counts = Counter(samples)
    print(child_counts)
    for child, count in child_counts.items():
        yield from sample(child, n=count)
