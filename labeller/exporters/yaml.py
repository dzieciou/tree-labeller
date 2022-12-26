import yaml
from anytree.exporter import DictExporter

from labeller.types import RawCategory


def export(root: RawCategory, path: str):
    assert root != None
    assert path.endswith(".yaml")
    dct = DictExporter().export(root)
    with open(path, "w") as out:
        yaml.dump(dct, stream=out, default_flow_style=False, sort_keys=False)
