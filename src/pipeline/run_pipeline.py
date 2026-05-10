"""End-to-end pipeline orchestration."""

from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from correction.iterative_refinement import IterativeRefiner
from correction.factory import build_corrector
from evaluation.experiments import save_metrics
from evaluation.metrics import evaluate
from ocr.engine import MockJsonOCREngine
from review.highlighter import ReviewHighlighter
from risk.calibrator import RiskCalibrator
from risk.scorer import RiskScorer
from utils.io import read_json, read_yaml, write_json, write_text
from utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)


def run_pipeline(
    project_root: Path,
    run_label: str | None = None,
    provider_override: dict[str, Any] | None = None,
) -> dict[str, str]:
    config_dir = project_root / "configs"
    default_cfg = read_yaml(config_dir / "default.yaml")
    ocr_cfg = read_yaml(config_dir / "ocr.yaml")
    llm_cfg = read_yaml(config_dir / "llm.yaml")
    eval_cfg = read_yaml(config_dir / "evaluation.yaml")
    if provider_override:
        llm_cfg.setdefault("correction", {}).setdefault("provider", {}).update(provider_override)

    setup_logging(default_cfg.get("logging", {}).get("level", "INFO"))

    sample_input_path = project_root / default_cfg["paths"]["sample_input"]
    sample_gt_path = project_root / default_cfg["paths"]["sample_ground_truth"]
    outputs_root = project_root / default_cfg["paths"]["outputs_root"]

    ocr_engine = MockJsonOCREngine(default_confidence=ocr_cfg["ocr"]["default_confidence"])
    ocr_document = ocr_engine.process(str(sample_input_path))

    original_tokens = [t.text for t in ocr_document.tokens]
    confidences = [t.confidence for t in ocr_document.tokens]

    risk_scorer = RiskScorer(
        medium_threshold=eval_cfg["risk"]["medium_threshold"],
        high_threshold=eval_cfg["risk"]["high_threshold"],
        calibrator=RiskCalibrator(scale=eval_cfg["risk"]["calibrator_scale"]),
    )
    refiner = IterativeRefiner(
        corrector=build_corrector(llm_cfg["correction"]),
        risk_scorer=risk_scorer,
        max_iterations=llm_cfg["correction"]["max_iterations"],
        early_stop_risk_threshold=llm_cfg["correction"]["early_stop_risk_threshold"],
    )
    iterations = refiner.run(initial_tokens=original_tokens, base_confidences=confidences)
    final_iteration = iterations[-1]

    suffix = f"_{run_label}" if run_label else ""
    corrected_text_path = outputs_root / "corrected_text" / f"{ocr_document.document_id}{suffix}_corrected.txt"
    write_text(corrected_text_path, final_iteration.correction_result.corrected_text)

    iteration_report_path = outputs_root / "corrected_text" / f"{ocr_document.document_id}{suffix}_iterations.json"
    write_json(
        iteration_report_path,
        {
            "document_id": ocr_document.document_id,
            "iterations": [
                {
                    "iteration_index": item.iteration_index,
                    "corrected_text": item.correction_result.corrected_text,
                    "changes": [asdict(change) for change in item.correction_result.changes],
                    "document_risk": item.risk_summary.document_risk_score,
                }
                for item in iterations
            ],
        },
    )

    highlighter = ReviewHighlighter()
    review_html_path = outputs_root / "highlighted_reviews" / f"{ocr_document.document_id}{suffix}_review.html"
    highlighter.write_html(
        document_id=ocr_document.document_id,
        token_risks=final_iteration.risk_summary.token_risks,
        output_path=review_html_path,
    )

    ground_truth = read_json(sample_gt_path)
    metrics = evaluate(
        reference=ground_truth["text"],
        raw=ocr_document.raw_text,
        corrected=final_iteration.correction_result.corrected_text,
    )
    metrics_path = outputs_root / "metrics" / f"{ocr_document.document_id}{suffix}_metrics.json"
    save_metrics(metrics, metrics_path)

    logger.info("Pipeline complete for %s", ocr_document.document_id)
    return {
        "document_id": ocr_document.document_id,
        "corrected_text_path": str(corrected_text_path),
        "review_html_path": str(review_html_path),
        "metrics_path": str(metrics_path),
        "iteration_report_path": str(iteration_report_path),
    }


def load_latest_outputs(project_root: Path, document_id: str) -> dict[str, Path]:
    outputs_root = project_root / "outputs"
    corrected_path = outputs_root / "corrected_text" / f"{document_id}_corrected.txt"
    review_path = outputs_root / "highlighted_reviews" / f"{document_id}_review.html"
    metrics_path = outputs_root / "metrics" / f"{document_id}_metrics.json"

    required = {
        "corrected": corrected_path,
        "review": review_path,
        "metrics": metrics_path,
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        missing_str = ", ".join(missing)
        raise FileNotFoundError(f"Missing expected output artifacts: {missing_str}")

    return required
    if provider_override:
        llm_cfg.setdefault("correction", {}).setdefault("provider", {}).update(provider_override)
