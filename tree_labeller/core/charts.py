from termgraph.termgraph import chart, AVAILABLE_COLORS

from .task import LabellingTask
from .types import TO_REJECT_LABEL, TO_SKIP_LABEL


def _get_label_name(label: str) -> str:
    return {
        TO_REJECT_LABEL: f"({TO_REJECT_LABEL}) Rejected",
        TO_SKIP_LABEL: f"({TO_SKIP_LABEL}) Skipped",
    }.get(label, label)


class Charts:
    def __init__(self, task: LabellingTask):
        self.task = task

    def print_manual_labels_coverage(self):
        coverage = sorted(
            self.task.n_products_per_manual_label.items(),
            key=lambda label_count: (label_count[1], label_count[0]),
        )
        labels = [_get_label_name(label_count[0]) for label_count in coverage]
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
        good = self.task.n_products_per_good_label
        ambiguous = self.task.n_products_per_ambiguous_label
        coverage = {
            label: (good[label], ambiguous[label])
            for label in self.task.config.allowed_provided_labels | {TO_REJECT_LABEL}
        }
        coverage = sorted(
            coverage.items(),
            key=lambda label_count: (label_count[1][0], label_count[0]),
        )
        labels = [_get_label_name(label_count[0]) for label_count in coverage]
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
