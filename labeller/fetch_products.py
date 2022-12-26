from labeller.exporters.yaml import export

from labeller.parsers.frisco import FriscoTreeParser
from labeller.parsers.yaml import YamlTreeParser


def fetch():
    parser = FriscoTreeParser()
    root, _ = parser.parse_tree("https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl")
    export(root, "products.yaml")
    yaml_parser = YamlTreeParser()
    yaml_parser.parse_tree("products.yaml")

if __name__ == "__main__":
    fetch()