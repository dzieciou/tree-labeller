#!/usr/bin/env python
import logging

import fire

from tree_labeller.core.charts import Charts
from tree_labeller.core.progress import ProgressTracker
from tree_labeller.core.task import (
    LabellingTask,
)
from tree_labeller.core.types import TO_REJECT_LABEL, TO_SKIP_LABEL

logging.basicConfig(level=logging.INFO)

PRODUCTS_PATH = "products.yaml"


def label(
    dir: str,
    sample: int = 100,
):

    task = LabellingTask.from_dir(dir)
    task.predict_labels(sample)

    tracker = ProgressTracker(task)
    print("\nHere is the labelling progress.py made so far:\n")
    # FIXME If we don't save stats (e.g. with check_only flag) they won't be seen here
    #       perhaps we should get that information from memory, not from file
    print(tracker.update_progress())

    charts = Charts(task)
    print("\nHere is how many products you labelled for each department so far: \n")
    charts.print_manual_labels_coverage()

    print(
        "\nHere is how many products we predicted for each department so far "
        "(good predicted vs. ambiguous) : \n"
    )
    charts.print_predicted_labels_coverage()

    path = task.try_save_good_predicted_labels()
    if path:
        print(
            f"\nI have saved {task.n_good_labels} product labels to {path}.\n\n"
            f"You can use them for training a classifier "
            f"(don't forget to skip rejected products).\n"
        )

    path = task.try_save_labels_to_verify()
    if path:
        print(
            f"\nI have selected {task.n_selected_for_verification_labels} out of "
            f"{task.n_requires_verification_labels} product labels to verify.\n\n"
            f"Please review them in {path} and repeat prediction.\n\n"
            f"Remember you don't need to label all of them if you are not sure about the label "
            f"(you can mark them with {TO_SKIP_LABEL}).\n"
            f"If you don't want to label the product (e.g., because the product or its category is"
            f" not present in a given task), then mark them with {TO_REJECT_LABEL}"
        )


def cli():
    fire.Fire(label)


if __name__ == "__main__":
    cli()
