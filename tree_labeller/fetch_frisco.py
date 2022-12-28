#!/usr/bin/env python
import os.path

import fire

from tree_labeller.exporters.yaml import export_tree

from tree_labeller.parsers.frisco import FriscoTreeParser

TREE_URL = "https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl"

TREE_YAML = "products.yaml"


def fetch():
    parser = FriscoTreeParser()
    root, _ = parser.parse_tree(TREE_URL)
    path = os.path.abspath(TREE_YAML)
    export_tree(root, path)
    print(f"Saved product dump to: {path}")


def cli():
    fire.Fire(fetch)


if __name__ == "__main__":
    cli()
