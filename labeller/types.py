from dataclasses import dataclass
from typing import Set, Optional

from anytree import NodeMixin, PreOrderIter

TO_REJECT_LABEL = "!"
TO_SKIP_LABEL = "?"
START_TIME_FORMAT = "%Y%m%d%H%M%S"
ProductName = str
ProductId = int
Label = str


@dataclass
class Labels:
    """Describes labelling of a single node of a tree."""

    manual: Label = None
    predicted: Set[Label] = None
    selected: bool = False

    @property
    def is_ambiguous(self):
        return self.predicted is not None and len(self.predicted) > 1

    @property
    def is_missing(self):
        return not self.predicted

    @property
    def to_skip(self):
        return self.manual == TO_SKIP_LABEL

    @property
    def to_reject(self):
        return self.manual == TO_REJECT_LABEL

    @property
    def is_good(self):
        return self.predicted is not None and len(self.predicted) == 1

    @property
    def good_label(self) -> Optional[str]:
        return next(iter(self.predicted)) if self.is_good else None

    @property
    def ambiguous(self) -> Set[str]:
        return self.predicted if self.is_ambiguous else set()

    def requires_verification(self):
        return self.is_missing or self.is_ambiguous

    @property
    def to_verify(self):
        if self.predicted:
            return self.predicted
        if self.manual:
            return {self.manual}
        return {}


class RawCategory(NodeMixin):
    def __init__(self, name: str, id: str, parent: "RawCategory" = None):
        self.name = name
        self.id = id
        self.parent = parent

    def __copy__(self):
        return RawCategory(self.name, self.id)

    @property
    def long_name(self):
        return ">".join(n.name for n in self.path)

    def __str__(self):
        return self.long_name

    def __repr__(self):
        return self.long_name

    def add_product(self, product: "Product"):
        self.products.add(product)

    @property
    def products(self):
        return [node for node in self.leaves if isinstance(node, RawProduct)]

    @property
    def categories(self):
        return [node for node in PreOrderIter(self.root) if isinstance(node, RawCategory)]

    @property
    def n_products(self):
        return len(self.products)

    @property
    def n_categories(self):
        return len(self.products)


class Category(RawCategory):

    def __init__(self, name: str, id: str, parent: "Category" = None):
        super().__init__(name, id, parent)
        self.labels = Labels()

class RawProduct(NodeMixin):
    id: ProductId
    name: ProductName
    brand: str

    def __init__(
        self, id: ProductId, name: ProductName, brand: str, category: RawCategory
    ):
        self.id = id
        self.name = name
        self.brand = brand
        self.parent = category

    @property
    def category(self):
        return self.parent

    @property
    def category_id(self):
        return self.category.id

    @property
    def category_name(self):
        return self.category.long_name

    @property
    def product_id(self):
        return self.id

class Product(RawProduct):
    labels: Labels

    def __init__(
        self, id: ProductId, name: ProductName, brand: str, category: Category
    ):
        super().__init__(id, name, brand, category)
        self.labels = Labels()