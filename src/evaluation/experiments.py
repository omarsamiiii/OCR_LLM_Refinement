"""Helpers for experiment evaluation and reporting."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from evaluation.metrics import EvaluationMetrics
from utils.io import write_json


def save_metrics(metrics: EvaluationMetrics, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, asdict(metrics))
