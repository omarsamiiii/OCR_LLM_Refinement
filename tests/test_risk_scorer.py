from risk.calibrator import RiskCalibrator
from risk.scorer import RiskScorer


def test_risk_scorer_assigns_levels() -> None:
    scorer = RiskScorer(
        medium_threshold=0.33,
        high_threshold=0.66,
        calibrator=RiskCalibrator(scale=1.0),
    )
    summary = scorer.score(
        tokens=["quick", "qu1et", "ok"],
        confidences=[0.95, 0.45, 0.99],
        changed_indices={1},
    )

    assert len(summary.token_risks) == 3
    assert summary.token_risks[1].level in {"medium", "high"}
