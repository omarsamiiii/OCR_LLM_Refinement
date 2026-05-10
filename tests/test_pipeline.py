from pathlib import Path

from pipeline.run_pipeline import run_pipeline


def test_pipeline_runs_end_to_end() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_pipeline(
        project_root=root,
        run_label="test",
        provider_override={"name": "mock"},
    )

    assert Path(result["corrected_text_path"]).exists()
    assert Path(result["review_html_path"]).exists()
    assert Path(result["metrics_path"]).exists()
