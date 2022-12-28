#!/usr/bin/env python
import fire

from tree_labeller.exporters.yaml import export_tree
from tree_labeller.parsers.frisco import FriscoTreeParser

TREE_URL = "https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl"


def fetch():
    parser = FriscoTreeParser()
    root, _ = parser.parse_tree(TREE_URL)
    export_tree(root)

def cli():
    fire.Fire(fetch)


if __name__ == "__main__":
    cli()
