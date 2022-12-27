#!/usr/bin/env python
import os.path

import fire

from labeller.exporters.yaml import export

from labeller.parsers.frisco import FriscoTreeParser

DEFAULT_FILENAME = "products.yaml"


def fetch():
    parser = FriscoTreeParser()
    root, _ = parser.parse_tree(
        "https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl"
    )
    path = os.path.abspath(DEFAULT_FILENAME)
    export(root, path)
    print(f"Saved product dump to: {path}")

def cli():
    fire.Fire(fetch)


if __name__ == "__main__":
    cli()