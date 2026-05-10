"""Evaluate raw OCR text and corrected text against ground truth."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluation.metrics import evaluate
from utils.io import read_json


if __name__ == "__main__":
    sample_input = read_json(ROOT / "data" / "samples" / "sample_ocr_input.json")
    sample_gt = read_json(ROOT / "data" / "samples" / "sample_ground_truth.json")

    raw_metrics = evaluate(sample_gt["text"], sample_input["text"], sample_input["text"])

    corrected_text_path = ROOT / "outputs" / "corrected_text" / "doc-001_corrected.txt"
    if corrected_text_path.exists():
        corrected_text = corrected_text_path.read_text(encoding="utf-8")
        corrected_metrics = evaluate(sample_gt["text"], sample_input["text"], corrected_text)
    else:
        corrected_metrics = None

    print("Baseline metrics (raw OCR as hypothesis):")
    print(raw_metrics)
    if corrected_metrics is not None:
        print("\nCorrected metrics:")
        print(corrected_metrics)
    else:
        print("\nNo corrected output found yet. Run scripts/run_sample_pipeline.py first.")
