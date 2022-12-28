from anytree import NodeMixin, PreOrderIter


def internals(root: NodeMixin):
    return (node for node in PreOrderIter(root) if not node.is_leaf)
