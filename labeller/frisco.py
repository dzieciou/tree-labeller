"""
Prepares training data from frisco
"""
import hashlib
import json
import logging
from itertools import chain
from typing import Dict, Any
from typing import Generator

from tqdm import tqdm

from labeller.shop import Product, Category, Shop
from labeller.tree.utils import internals
import fsspec as fs

Json = Dict[str, Any]

CACHE_OPTIONS = {
    "cache_storage": "./tmp/frisco",
    "cache_check": False,
    "expiry_time": False,
}


class FriscoShop(Shop):
    @classmethod
    def from_dump(cls, path: str):
        logging.info(f"Downloading Frisco products dump form {path}...")
        with fs.open(
            "filecache::" + path,
            filecache=CACHE_OPTIONS,
        ) as f:
            content = f.read()
        content_hash, content = hashlib.md5(content).hexdigest(), json.loads(content)
        categories = cls._parse_categories(content)
        cls._attach_products(content, categories)
        return cls(categories, content_hash)

    @classmethod
    def _parse_categories(cls, content: Json) -> Category:
        def parse_one(category: Json):
            name = category["name"]["pl"]
            parent_path = category["parentPath"].split(",")
            id = int(parent_path[0])
            parent_id = int(parent_path[1]) if len(parent_path) > 1 else None
            yield Category(name, id=id, parent_id=parent_id)
            if "children" in category:
                for child in category["children"]:
                    yield from parse_one(child)

        nodes = chain(
            node for category in content["categories"] for node in parse_one(category)
        )
        nodes = {node.id: node for node in nodes}
        root = Category("categories", id=0)
        for node in tqdm(nodes.values(), desc="Parsing categories"):
            node.parent = nodes.get(node.parent_id, root)
        return root

    @classmethod
    def _attach_products(
        cls, content: Json, categories_root: Category
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
