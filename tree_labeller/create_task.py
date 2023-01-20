#!/usr/bin/env python

import logging
from typing import Set

from tree_labeller.core.task import LabellingTask

logging.basicConfig(level=logging.INFO)


def create_task(dir: str, tree: str, allowed_labels: Set[str]):
    LabellingTask.initialize(
        dir=dir, tree_path=tree, allowed_provided_labels=allowed_labels
    )


def cli():
    import fire
    fire.Fire(create_task)


if __name__ == "__main__":
    cli()
