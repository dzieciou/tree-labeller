import sys
from typing import Optional, Union, Dict

import yaml
from anytree.exporter import DictExporter

from tree_labeller.core.types import Category

# FIXME This is ugly, perhaps we should change implementation of Product or introduce to_dict there
def custom(key_values) -> Dict:
    d = {}
    for k, v in key_values:
        if k == "attrs":
            d = {**d, **v}
        else:
            d[k] = v
    return d


def export_tree(tree: Category, path: Optional[str] = None):
    assert tree != None
    dct = DictExporter(dictcls=custom).export(tree)

    if path:
        assert path.endswith(".yaml")
        out = open(path, "w")
    else:
        out = sys.stdout
    with out:
        yaml.dump(dct, stream=out, default_flow_style=False, sort_keys=False)
