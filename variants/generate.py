#!/usr/bin/env python

import csv
import logging
from collections import defaultdict
from functools import lru_cache
from typing import Iterable, Tuple, Dict

import fire
import spacy
from spacy.tokens import Doc
from tqdm import tqdm

from labeller.shop import TO_REJECT_LABEL, Label

logging.basicConfig(level=logging.INFO)

logging.info("Loading spacy model...")
nlp = spacy.load("pl_core_news_sm", disable=["ner"])


def generate_product_variants(doc: Doc):
    yield doc[0].lemma_.lower()  # pomidor
    yield doc[0].text.lower()  # pomidory
    yield doc[0:2].text.lower()  # "earl grey"


@lru_cache(1000)
def generate_category_variants(name: str):
    doc = nlp(name)
    yield doc[0:2].text.lower()  # "earl grey"
    for token in doc:
        if token.is_punct:
            continue
        if token.pos_ == "POS" and token.morph.to_dict()["Case"] != "Nom":
            continue
        yield token.lemma_.lower()  # pomidor
        yield token.text.lower()  # pomidory


def normalize(text: str) -> str:
    return text.lower().strip()


ProductName = str
ProductDoc = Doc
Category = str
Brand = str
LabelledProduct = Tuple[ProductDoc, Category, Brand, Label]


def load(path: str):
    def parse(rows):
        parsed = [
            (row["name"], row["category"], row["brand"], row["label"])
            for row in rows
            if row["label"] != TO_REJECT_LABEL
        ]
        products, categories, brands, labels = zip(*parsed)
        products = nlp.pipe(products, batch_size=512, n_process=4)
        return zip(products, categories, brands, labels)

    with open(path) as f:
        rows = csv.DictReader(f, delimiter="\t")
        rows = tqdm(parse(rows), desc="Parsing rows")
        yield from rows


def generate_variants(rows: Iterable[LabelledProduct]) -> Dict[ProductName, Label]:

    univocal = {}
    variants = defaultdict(set)

    n_rows = 0
    for product_doc, category, brand, label in rows:
        n_rows += 1
        name = normalize(product_doc.text)
        univocal[name] = label
        variants[name].add(label)

        # Ludwik, Sidulux
        brand = normalize(brand)
        variants[brand].add(label)

        for variant in generate_product_variants(product_doc):
            variant = normalize(variant)
            variants[variant].add(label)

        # Warzywa i owoce>Pomidory>Pomidory amerykańskie
        most_specific_category = category.split(">")[-1]
        for variant in generate_category_variants(most_specific_category):
            variant = normalize(variant)
            variants[variant].add(label)

    # Use only variants that are non-ambiguous
    for variant, labels in variants.items():
        if len(labels) == 1:
            univocal[variant] = next(iter(labels))

    logging.info(f"Generated {len(univocal.keys())} out of {n_rows} labelled products.")

    return univocal


def generate(path: str, output_path: str):
    """
    Generates TSV files with different variants of labelled prodsucts.
    """

    labelled_products = load(path)
    labelled_variants = generate_variants(labelled_products)
    with open(output_path, "w") as f:
        output = csv.DictWriter(f, fieldnames=["name", "label"], delimiter="\t")
        output.writeheader()
        labelled_variants = sorted(labelled_variants.items())
        for product, label in labelled_variants:
            output.writerow(
                {
                    "name": product,
                    "label": label,
                }
            )
    logging.info(f"Saved variants to {output_path}.")


def cli():
    fire.Fire(generate)


if __name__ == "__main__":
    cli()
