"""
Prepares training data from frisco
"""
import hashlib
import json
import logging
from typing import Dict, Any, Tuple
from typing import Generator

import fsspec as fs
from tqdm import tqdm

from tree_labeller.core.types import Category, Product
from tree_labeller.parsers.treeparser import TreeParser, ContentHash
from tree_labeller.tree.utils import internals

ROOT_CATEGORY_NAME = "categories"

Json = Dict[str, Any]

CACHE_OPTIONS = {
    "cache_storage": "./tmp/frisco",
    "cache_check": False,
    "expiry_time": False,
}


class FriscoTreeParser(TreeParser):
    def parse_tree(self, path: str) -> Tuple[Category, ContentHash]:
        logging.info(f"Downloading Frisco products dump form {path}...")
        with fs.open(
            "filecache::" + path,
            filecache=CACHE_OPTIONS,
        ) as f:
            return self._parse_content(f.read())

    def _parse_content(self, content: str) -> Tuple[Category, ContentHash]:
        content_hash = hashlib.md5(content).hexdigest()
        content = json.loads(content)
        tree = self._parse_categories(content)
        self._attach_products(tree, content)
        return tree, content_hash

    def _parse_categories(self, content: Json) -> Category:
        def parse_one(category: Json):
            name = category["name"]["pl"]
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

        root = Category(ROOT_CATEGORY_NAME, id=0)
        for node, parent_id in tqdm(indexed_nodes.values(), desc="Parsing categories"):
            parent, _ = indexed_nodes.get(parent_id, (root, None))
            node.parent = parent

        return root

    def _attach_products(
        self, categories_root: Category, content: Json
    ) -> Generator[Product, None, None]:
        categories_by_id = {
            int(category.id): category
            for category in tqdm(internals(categories_root), desc="Indexing categories")
        }
        for product in tqdm(content["products"], desc="Parsing products"):
            if (
                "primaryCategory" in product
                and "parentId" in product["primaryCategory"]
            ):
                category_id = int(product["primaryCategory"]["parentId"])
                brand = product["brand"]
                subbrand = product.get("subbrand")
                if subbrand:
                    brand = f"{brand} {subbrand}"

                Product(
                    id=product["id"],
                    name=product["name"]["pl"].strip(),
                    brand=brand,
                    category=categories_by_id[int(category_id)],
                )
