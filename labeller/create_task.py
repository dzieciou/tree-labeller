#!/usr/bin/env python

import os
import shutil
from typing import Set

import fire
import yaml


def create_task(dir: str, tree: str, allowed_labels: Set[str]):
    dir = os.path.abspath(dir)
    try:
        os.makedirs(dir, exist_ok=False)
    except FileExistsError:
        print(f"Directory {dir} already exists. Perhaps this is a previous task?")
        return

    dest_tree_path = os.path.join(dir)
    shutil.copy(tree, dest_tree_path)
    config = {"dir": dir, "tree": tree, "allowed_labels": allowed_labels}
    with open(os.path.join(dir, "config.yaml"), "w") as out:
        yaml.dump(config, out)


if __name__ == "__main__":
    fire.Fire(create_task)
