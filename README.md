# A Human-in-the-Loop OCR Refinement Framework Using Iterative LLM Correction and Uncertainty-Guided Verification

## Motivation
This repository is an MSc thesis prototype for building a practical OCR refinement workflow where automatic correction and selective human verification work together. The objective is to reduce OCR errors while keeping human effort focused on uncertain regions.

## Current MVP Status
This first version provides a runnable, extensible pipeline with:
- Mock OCR loading from JSON
- Deterministic mock LLM-style correction heuristics
- Iterative refinement with early stopping
- Heuristic residual risk scoring with calibration placeholder
- HTML risk highlighting for human review
- Evaluation against ground truth (CER, WER, token-level precision/recall/F1)
- Scripts and tests for reproducible runs

## Workflow
1. Load sample OCR input
2. Parse into `OCRDocument` and `OCRToken` objects
3. Iteratively correct text (`CorrectionResult`, `IterationResult`)
4. Score token/document residual risk (`RiskScore`)
5. Generate review artifact (`ReviewArtifact`) with color-coded risk
6. Compute evaluation metrics
7. Save artifacts under `outputs/`

## Repository Structure
```text
human-in-the-loop-ocr/
  configs/                 # YAML configs for pipeline, OCR, correction, evaluation
  data/samples/            # Sample OCR input + ground truth
  docs/                    # Thesis notes, meetings, diagrams, papers
  notebooks/               # Placeholder analysis notebooks
  src/
    ocr/                   # OCR models + engine interface/mock engine
    correction/            # Corrector + iterative refinement loop
    risk/                  # Risk scoring + calibration placeholder
    review/                # HTML highlighter + feedback hooks
    evaluation/            # Metrics and experiment artifact helpers
    pipeline/              # End-to-end orchestration
    utils/                 # IO/logging/alignment utilities
    prompts/               # Future LLM prompt templates
  scripts/                 # Runnable scripts for pipeline/evaluation/highlighting
  tests/                   # Pytest coverage of core behavior
  outputs/                 # Generated artifacts (created by runs)
```

## Installation
Python 3.11+ is required.

```bash
cd human-in-the-loop-ocr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run the Sample Pipeline
```bash
python scripts/run_sample_pipeline.py
```

Expected artifacts:
- `outputs/corrected_text/doc-001_corrected.txt`
- `outputs/corrected_text/doc-001_iterations.json`
- `outputs/highlighted_reviews/doc-001_review.html`
- `outputs/metrics/doc-001_metrics.json`

## Run Evaluation Script
```bash
python scripts/evaluate_baseline.py
```

## Regenerate Highlighted HTML
```bash
python scripts/generate_highlighted_output.py
```

## Run Tests
```bash
pytest -q
```

## Design Notes
- Uses `pathlib`, type hints, dataclasses, and logging.
- Keeps logic deterministic and easy to inspect for thesis reporting.
- Uses minimal dependencies (`PyYAML`, `pytest`).
- Architecture is intentionally modular to swap in real OCR/LLM components later.

## Current Limitations
- OCR is mock JSON input (no image OCR yet).
- Corrector uses deterministic heuristics, not real LLM APIs.
- Risk scorer is heuristic and lightly calibrated.
- No UI yet; human feedback is logged through data hooks only.

## Future Roadmap
1. Integrate real OCR backends (e.g., Tesseract, cloud OCR APIs).
2. Add real LLM correction with prompt/version management.
3. Add calibration with held-out human-labeled error/risk data.
4. Build interactive reviewer UI for token-level corrections.
5. Add experiment tracking, ablations, and richer visualization notebooks.

## Suggested First Commit Message
`Initial scaffold for human-in-the-loop OCR thesis prototype`
