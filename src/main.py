"""Entry point for running the OCR refinement pipeline."""

from pathlib import Path

from pipeline.run_pipeline import run_pipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    result = run_pipeline(project_root=project_root)
    print(f"Pipeline completed for document: {result['document_id']}")
    print(f"Corrected text saved to: {result['corrected_text_path']}")
    print(f"Review HTML saved to: {result['review_html_path']}")
    print(f"Metrics saved to: {result['metrics_path']}")
