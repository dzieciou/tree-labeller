import logging

from labeller.types import Category


def remove_leaf_categories_without_product(root: Category):
    removed = True
    n_removed = 0
    while removed:
        removed = False
        for leaf in root.leaves:
            if isinstance(leaf, Category):
                leaf.parent = None
                removed = True
                n_removed += 1
    logging.debug(f"Removed {n_removed} categories without product.")
