import json
import logging
from typing import Optional

from jsonlines import jsonlines
from tabulate import tabulate
from termgraph.termgraph import chart, AVAILABLE_COLORS

from labeller.task import LabellingTask
from labeller.types import TO_REJECT_LABEL, TO_SKIP_LABEL


class Reporter:
    def __init__(self, task: LabellingTask):
        self.task = task

    def save_stats(self, path: Optional[str] = None):
        if path is None:
            path = self.to_path(
                "stats",
                "json",
            )
        with open(path, "w") as f:
            json.dump(self.stats, f, indent=2, cls=CustomEncoder)
        logging.info(f"Saved stats to {path}.")

    def update_all_stats(self, path: Optional[str] = None):
        if path is None:
            path = self.all_stats_path

        iteration_stats = {
            "start_time": self.config.start_time.isoformat(),
            "iteration": self.state.iteration,
            "stats": self.stats,
        }
        encoder = CustomEncoder()
        with jsonlines.open(path, "a", dumps=encoder.encode) as writer:
            writer.write(iteration_stats)
        logging.info(f"Updated all iterations stats in {path}.")

    @property
    def progress_table(self):
        rows = []
        with jsonlines.open(self.all_stats_path) as reader:
            for iteration_stats in reader:
                row = [
                    iteration_stats["iteration"],
                    iteration_stats["stats"]["progress"]["manual"],
                    iteration_stats["stats"]["progress"]["univocal"],
                    iteration_stats["stats"]["progress"]["ambiguous"],
                    iteration_stats["stats"]["progress"]["missing"],
                    iteration_stats["stats"]["shop"]["n_products"],
                    iteration_stats["stats"]["progress"]["allowed_labels"],
                ]
                rows.append(row)

        return tabulate(
            rows,
            headers=[
                "Iteration",
                "Manual",
                "Univocal",
                "Ambiguous",
                "Missing",
                "Total",
                "Allowed Labels",
            ],
            floatfmt=".0%",
        )

    def print_manual_labels_coverage(self):
        coverage = sorted(
            self.n_products_per_manual_label.items(),
            key=lambda label_count: (label_count[1], label_count[0]),
        )
        labels = [get_label_name(label_count[0]) for label_count in coverage]
        data = [[label_count[1]] for label_count in coverage]
        args = {
            "histogram": False,
            "stacked": False,
            "different_scale": False,
            "width": 50,
            "no_labels": False,
            "no_values": False,
            "format": "{:.0f}",
            "suffix": "",
            "vertical": False,
        }
        chart([AVAILABLE_COLORS["blue"]], data, args, labels)

    def print_predicted_labels_coverage(self):
        good = self.n_products_per_good_label
        ambiguous = self.n_products_per_ambiguous_label
        coverage = {
            label: (good[label], ambiguous[label])
            for label in self.config.allowed_provided_labels | {TO_REJECT_LABEL}
        }
        coverage = sorted(
            coverage.items(),
            key=lambda label_count: (label_count[1][0], label_count[0]),
        )
        labels = [get_label_name(label_count[0]) for label_count in coverage]
        data = [[label_count[1][0], label_count[1][1]] for label_count in coverage]
        args = {
            "histogram": False,
            "stacked": True,
            "different_scale": False,
            "width": 50,
            "no_labels": False,
            "no_values": False,
            "format": "{:.0f}",
            "suffix": "",
            "vertical": False,
        }
        chart([AVAILABLE_COLORS["green"], AVAILABLE_COLORS["red"]], data, args, labels)


def get_label_name(label: str) -> str:
    return {
        TO_REJECT_LABEL: f"({TO_REJECT_LABEL}) Rejected",
        TO_SKIP_LABEL: f"({TO_SKIP_LABEL}) Skipped",
    }.get(label, label)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
