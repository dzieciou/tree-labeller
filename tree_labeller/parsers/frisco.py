"""
Prepares training data from frisco
"""
import json
import logging
from typing import Dict, Any, Literal

import fsspec as fs
from tqdm import tqdm

from tree_labeller.core.types import Category, Product
from tree_labeller.core.utils import remove_leaf_categories_without_product
from tree_labeller.parsers.treeparser import TreeParser
from tree_labeller.tree.utils import internals

Json = Dict[str, Any]

LANGUAGE_CODE = Literal["pl", "en"]
CACHE_OPTIONS = {
    "cache_storage": "./tmp/frisco",
    "cache_check": False,
    "expiry_time": False,
}


class FriscoTreeParser(TreeParser):
    def __init__(
        self, root_category_name: str = "categories", lang: LANGUAGE_CODE = "pl"
    ):
        self.root_category_name = root_category_name
        self.lang = lang

    def parse_tree(self, urlpath: str) -> Category:
        logging.info(f"Downloading Frisco products dump form {urlpath}...")
        with fs.open(
            "filecache::" + urlpath,
            filecache=CACHE_OPTIONS,
        ) as f:
            tree = self._parse_content(f.read())
            remove_leaf_categories_without_product(tree)
            return tree

    def _parse_content(self, jsonString: str) -> Category:
        jsonString = json.loads(jsonString)
        tree = self._parse_categories(jsonString)
        self._attach_products(tree, jsonString)
        return tree

    def _parse_categories(self, content: Json) -> Category:
        def parse_one(category: Json):
            name = category["name"][self.lang]
            parent_path = category["parentPath"].split(",")
            id = int(parent_path[0])
            parent_id = int(parent_path[1]) if len(parent_path) > 1 else None
            yield Category(name, id=id), parent_id
            if "children" in category:
                for child_json in category["children"]:
                    yield from parse_one(child_json)

        indexed_nodes = {}
        for category in content["categories"]:
            for node, parent_id in parse_one(category):
                indexed_nodes[node.id] = (node, parent_id)

        root = Category(self.root_category_name, id=0)
        for node, parent_id in tqdm(indexed_nodes.values(), desc="Parsing categories"):
            parent, _ = indexed_nodes.get(parent_id, (root, None))
            node.parent = parent

        return root

    def _attach_products(self, tree: Category, content: Json):
        categories_by_id = {
            int(category.id): category
            for category in tqdm(internals(tree), desc="Indexing categories")
        }
        for product in tqdm(content["products"], desc="Parsing products"):
            if not (
                "primaryCategory" in product
                and "parentId" in product["primaryCategory"]
            ):
                continue

            category_id = int(product["primaryCategory"]["parentId"])
            brand = product["brand"]
            subbrand = product.get("subbrand")
            if subbrand:
                brand = f"{brand} {subbrand}"

            Product(
                id=product["id"],
                name=product["name"][self.lang].strip(),
                brand=brand,
                category=categories_by_id[int(category_id)],
            )
