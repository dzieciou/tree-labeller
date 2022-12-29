from typing import Tuple

import yaml

from tree_labeller.core.types import LabelableCategory, LabelableProduct
from tree_labeller.parsers.treeparser import TreeParser, ContentHash


class YamlTreeParser(TreeParser):
    def parse_tree(self, path: str) -> Tuple[LabelableCategory, ContentHash]:
        with open(path) as input:
            dct = yaml.full_load(input)
        return CustomDictImporter().import_(dct), None


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
            node = LabelableCategory(parent=parent, **attrs)
        else:
            try:
                node = LabelableProduct(category=parent, **attrs)
            except TypeError:
                # Some leaves might be not products but categories without products
                return parent
        for child in children:
            self.__import(child, parent=node)
        return node
