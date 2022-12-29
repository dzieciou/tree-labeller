import sys
from typing import Optional

import yaml
from anytree.exporter import DictExporter

from tree_labeller.core.types import Category


def export_tree(tree: Category, path: Optional[str] = None):
    assert tree != None
    dct = DictExporter().export(tree)

    if path:
        assert path.endswith(".yaml")
        out = open(path, "w")
    else:
        out = sys.stdout
    with out:
        yaml.dump(dct, stream=out, default_flow_style=False, sort_keys=False)
