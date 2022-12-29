from tree_labeller.parsers.yaml import YamlTreeParser

import pytest

def test_parse(tmp_path):
    yaml_doc = """
name: categories
id: 1
children:
- name: Alcoholic Drinks
  id: 11
  children:
  - name: Whiskies
    id: 111
    children:
    - name: Jack Daniel's
      id: 1111
    - name: Johnnie Walker's
      id: 1112
  - name: Wines
    id: 112
    children:
    - name: Cabernet Sauvignon
      id: 1121
  - name: Beers
    id: 113
    children:
    - name: Guinness
      id: 1131
    """
    path = tmp_path / "doc.yaml"
    with open(path, "w") as f:
        f.write(yaml_doc)
    tree = YamlTreeParser().parse_tree(path)
    print(tree)
    # TODO complete