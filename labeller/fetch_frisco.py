#!/usr/bin/env python

from labeller.exporters.yaml import export

from labeller.parsers.frisco import FriscoTreeParser


def fetch():
    parser = FriscoTreeParser()
    root, _ = parser.parse_tree(
        "https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl"
    )
    export(root, "products.yaml")


if __name__ == "__main__":
    fetch()
