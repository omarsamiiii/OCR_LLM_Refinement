"""Regenerate highlighted HTML review artifact from latest corrected output."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocr.engine import MockJsonOCREngine
from review.highlighter import ReviewHighlighter
from risk.calibrator import RiskCalibrator
from risk.scorer import RiskScorer
from utils.io import read_yaml


if __name__ == "__main__":
    default_cfg = read_yaml(ROOT / "configs" / "default.yaml")
    eval_cfg = read_yaml(ROOT / "configs" / "evaluation.yaml")
    ocr_cfg = read_yaml(ROOT / "configs" / "ocr.yaml")

    sample_input_path = ROOT / default_cfg["paths"]["sample_input"]
    engine = MockJsonOCREngine(default_confidence=ocr_cfg["ocr"]["default_confidence"])
    doc = engine.process(str(sample_input_path))

    corrected_path = ROOT / "outputs" / "corrected_text" / f"{doc.document_id}_corrected.txt"
    if not corrected_path.exists():
        raise FileNotFoundError("Corrected text not found. Run run_sample_pipeline.py first.")

    corrected_tokens = corrected_path.read_text(encoding="utf-8").split()
    confidences = [t.confidence for t in doc.tokens]
    changed_indices = {i for i, (a, b) in enumerate(zip([t.text for t in doc.tokens], corrected_tokens)) if a != b}

    scorer = RiskScorer(
        medium_threshold=eval_cfg["risk"]["medium_threshold"],
        high_threshold=eval_cfg["risk"]["high_threshold"],
        calibrator=RiskCalibrator(scale=eval_cfg["risk"]["calibrator_scale"]),
    )
    summary = scorer.score(corrected_tokens, confidences, changed_indices)

    out_path = ROOT / "outputs" / "highlighted_reviews" / f"{doc.document_id}_review.html"
    artifact = ReviewHighlighter().write_html(doc.document_id, summary.token_risks, out_path)
    print(f"Regenerated review file: {artifact.html_path}")
