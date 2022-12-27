#!/usr/bin/env python

from typing import Set

import fire

from labeller.labelling_task import LabellingTask


def create_task(dir: str, tree: str, allowed_labels: Set[str]):
    LabellingTask.initialize(dir, tree, allowed_labels)


def cli():
    fire.Fire(create_task)


if __name__ == "__main__":
    cli()
