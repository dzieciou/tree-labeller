from collections import defaultdict

from anytree import NodeMixin, PostOrderIter, PreOrderIter, SymlinkNode, AnyNode
#from fastcache import clru_cache
from functools import lru_cache
from tqdm import tqdm


# TODO Use Node instead of AnyNode


def select_distant_leaves(root: NodeMixin, n: int):
    """
    Find n leaves at that farthest apart in a given arbitrary tree.

    Uses a dynamic programming algorithm described in [1].

    :param root: root of a tree
    :param n: number of leaves to find
    :return: a set of leaves and a sum of distances between them

    [1]: https://cs.stackexchange.com/questions/134068/finding-n-farthest-leaves-in-a-tree
    """
    binary_tree = _to_binary_tree(root)
    leaves, total_distance = _select_distant_leaves_binary_tree(binary_tree, n)
    leaves = {leaf.target for leaf in leaves}
    return leaves


class BlankNode(AnyNode):
    pass


def _to_binary_tree(root: NodeMixin):
    """
    Converts arbitrary tree to a binary tree.

    Children from the original tree are encoded as a left child in binary tree and
    "edges" to left children have weight 1. Remaining "edges" (those to right children)
    have 0 weight. Technically, we encode weight of an edge as attribute of a target
    node of the edge.

    :param root:
            root of an arbitrary tree
    :return:
            a root of a new binary_tree
    """
    mapping = {}

    def create_link(node: NodeMixin, new_parent: SymlinkNode = None):
        link = SymlinkNode(target=node, parent=new_parent)
        mapping[node] = link
        return link

    create_link(root)
    for parent in PreOrderIter(root):
        # TODO interesujace, bo iteroojemy tu i po nizej po dzieciach
        #      czy to niepowoduje buga?
        new_parent = mapping[parent]
        children = parent.children
        if children:
            create_link(children[0], new_parent)
        for child in children[1:]:
            new_parent = BlankNode(parent=new_parent)
            create_link(child, new_parent)

    return mapping[root]


@lru_cache(maxsize=None)
def _count_leaves(node):
    return len(node.leaves)


def _select_distant_leaves_binary_tree(root: NodeMixin, n: int):
    """
    Find n leaves at that farthest apart in a given binary tree.

    :param root: root of a binary tree
    :param n: number of leaves to find
    :return: a set of leaves and a sum of distances between them
    """

    def weight(node: NodeMixin) -> float:
        if isinstance(node, SymlinkNode):
            # Get weight of node from the original tree, not the binary one
            node = node.target
        if isinstance(node, BlankNode):
            # This is intermediary node inserted during conversation to binary tree
            return 0.0
        # Promote nodes that represent main categories in the taxonomy
        # We don't want to get 10 nodes that are far away from all other nodes
        # but live in the same very deep subtree, e.g.,
        # we don't want to get 10 types of orange juice
        return 1000 / ((node.depth + 1) ** 20)

    assert n <= _count_leaves(
        root
    ), f"Cannot find {n} leaves out of {_count_leaves(root)} available"

    best_distances = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict))
    )
    selected_leaves = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict))
    )

    for node in tqdm(
        PostOrderIter(root),
        total=len(root.descendants) + 1,
        desc="Calculating distances",
    ):
        subtree_leaves = min(_count_leaves(node), n)
        remaining_leaves = _count_leaves(root) - _count_leaves(node)
        min_leaves = max(0, subtree_leaves - remaining_leaves)
        for j in range(min_leaves, subtree_leaves + 1):
            k = n - j
            if node.is_leaf:
                best_distances[node][j][k] = 0
                if j == 0:
                    selected_leaves[node][j][k] = set()
                else:
                    selected_leaves[node][j][k] = {node}
            elif len(node.children) == 1:
                child = node.children[0]
                best_distances[node][j][k] = best_distances[child][j][
                    k
                ] + j * k * weight(node)
                selected_leaves[node][j][k] = selected_leaves[child][j][k]
            else:
                left = node.children[0]
                right = node.children[1]
                distances = {}
                for j1 in range(j + 1):
                    j2 = j - j1
                    if j1 > _count_leaves(left) or j2 > _count_leaves(right) or j2 < 0:
                        continue  # TODO Perhaps there is a better way to handle that
                    distance = (
                        best_distances[left][j1][k + j2]
                        + best_distances[right][j2][k + j1]
                        + j1 * j2 * (weight(left) + weight(right))
                        + j * k * weight(node)
                    )
                    distances[j1] = distance
                best_distance = max(distances.values())
                best_distances[node][j][k] = best_distance
                best_j1 = next(
                    j1
                    for j1, distance in distances.items()
                    if distance == best_distance
                )
                best_j2 = j - best_j1
                selected_leaves[node][j][k] = (
                    selected_leaves[left][best_j1][k + best_j2]
                    | selected_leaves[right][best_j2][k + best_j1]
                )

    return selected_leaves[root][n][0], best_distances[root][n][0]
