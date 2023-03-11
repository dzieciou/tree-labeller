import json
import logging
import os

from jsonlines import jsonlines
from tabulate import tabulate

from .task import LabellingTask


class ProgressTracker:
    """
    Tracks labelling progress and provides statistics on it.
    """

    def __init__(self, task: LabellingTask):
        self.task = task

    def update_progress(self) -> str:
        fname = f"{self.task.state.iteration}-stats.json"
        path = os.path.join(self.task.dir, fname)
        self._save_iteration_stats(path)

        path = os.path.join(self.task.dir, "all-stats.jsonl")
        self._add_iteration_stats(path)
        return self._load_progress_table(path)

    def _save_iteration_stats(self, path: str):
        with open(path, "w") as f:
            json.dump(self.task.iteration_stats, f, indent=2, cls=_CustomEncoder)
        logging.info(f"Saved stats to {path}.")

    def _add_iteration_stats(self, path: str):
        iteration_stats = {
            "start_time": self.task.config.start_time.isoformat(),
            "iteration": self.task.state.iteration,
            "stats": self.task.iteration_stats,
        }
        encoder = _CustomEncoder()
        with jsonlines.open(path, "a", dumps=encoder.encode) as writer:
            writer.write(iteration_stats)
        logging.info(f"Updated all iterations stats in {path}.")

    def _load_progress_table(self, path: str) -> str:
        rows = []
        with jsonlines.open(path) as reader:
            for iteration_stats in reader:
                row = [
                    iteration_stats["iteration"],
                    iteration_stats["stats"]["progress.py"]["manual"],
                    iteration_stats["stats"]["progress.py"]["univocal"],
                    iteration_stats["stats"]["progress.py"]["ambiguous"],
                    iteration_stats["stats"]["progress.py"]["missing"],
                    iteration_stats["stats"]["tree"]["n_products"],
                    iteration_stats["stats"]["progress.py"]["allowed_labels"],
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


class _CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
