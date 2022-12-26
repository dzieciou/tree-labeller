from typing import Tuple

import yaml

from labeller.parsers.treeparser import TreeParser, ContentHash
from labeller.types import RawCategory, RawProduct


class YamlTreeParser(TreeParser):

    def parse_tree(self, path: str) -> Tuple[RawCategory, ContentHash]:
        with open(path) as input:
            dct = yaml.full_load(input)
        return CustomDictImporter().import_(dct)

class CustomDictImporter(object):

    def import_(self, data):
        """Import tree from `data`."""
        return self.__import(data)

    def __import(self, data, parent=None):
        assert isinstance(data, dict)
        assert "parent" not in data
        attrs = dict(data)
        children = attrs.pop("children", [])
        if children:
            return RawCategory(parent=parent, **attrs)
        else:
            return RawProduct(parent=parent, **attrs)


