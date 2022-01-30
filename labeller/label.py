#!/usr/bin/env python
import logging

import fire

from labeller.frisco import FriscoShop
from labeller.predict import predict_labels
from labeller.shop import TO_SKIP_LABEL, TO_REJECT_LABEL

logging.basicConfig(level=logging.INFO)

FRISCO_PRODUCTS_PATH = (
    "https://commerce.frisco.pl/api/v1/integration/feeds/public?language=pl"
)


def label(
    labels: str,
    allowed_labels: str,
    products_path: str = FRISCO_PRODUCTS_PATH,
    n_sample: int = 100,
):
    shop = FriscoShop.from_dump(products_path)
    shop.load_allowed_labels(allowed_labels)
    shop.init_manual_labels(labels)
    shop.remove_leaf_categories_without_product()

    predict_labels(shop, n_sample)

    shop.save_stats()
    shop.update_all_stats()

    print("\nHere is the labelling progress made so far:\n")
    # FIXME If we don't save stats (e.g. with check_only flag) they won't be seen here
    #       perhaps we should get that information from memory, not from file
    print(shop.progress_table)
    print("\nHere is how many products you labelled for each department so far: \n")
    shop.print_manual_labels_coverage()

    print(
        "\nHere is how many products we predicted for each department so far "
        "(good predicted vs. ambiguous) : \n"
    )
    shop.print_predicted_labels_coverage()

    path = shop.try_save_good_predicted_labels()
    if path:
        print(
            f"\nI have saved {shop.n_good_labels} product labels to {path}.\n\n"
            f"You can use them for training a classifier "
            f"(don't forget to skip rejected products).\n"
        )

    path = shop.try_save_labels_to_verify()
    if path:
        print(
            f"\nI have selected {shop.n_selected_for_verification_labels} out of "
            f"{shop.n_requires_verification_labels} product labels to verify.\n\n"
            f"Please review them in {path} and repeat prediction.\n\n"
            f"Remember you don't need to label all of them if you are not sure about the label "
            f"(you can mark them with {TO_SKIP_LABEL}).\n"
            f"If you don't want to label the product (e.g., because the product or its category is"
            f" not present in a given shop), then mark them with {TO_REJECT_LABEL}"
        )


def cli():
    fire.Fire(label)


if __name__ == "__main__":
    cli()
