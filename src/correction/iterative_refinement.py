"""Iterative OCR correction loop orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from correction.base import BaseCorrector, CorrectionResult
from risk.scorer import DocumentRiskSummary, RiskScorer


@dataclass(slots=True)
class IterationResult:
    """Captures one iteration outcome."""

    iteration_index: int
    correction_result: CorrectionResult
    risk_summary: DocumentRiskSummary


class IterativeRefiner:
    """Runs correction until convergence or risk threshold is met."""

    def __init__(
        self,
        corrector: BaseCorrector,
        risk_scorer: RiskScorer,
        max_iterations: int,
        early_stop_risk_threshold: float,
    ) -> None:
        self.corrector = corrector
        self.risk_scorer = risk_scorer
        self.max_iterations = max_iterations
        self.early_stop_risk_threshold = early_stop_risk_threshold

    def run(self, initial_tokens: list[str], base_confidences: list[float | None]) -> list[IterationResult]:
        tokens = initial_tokens[:]
        iterations: list[IterationResult] = []

        for idx in range(1, self.max_iterations + 1):
            correction = self.corrector.correct_tokens(tokens)
            risk_summary = self.risk_scorer.score(
                tokens=correction.corrected_tokens,
                confidences=base_confidences,
                changed_indices={change.token_index for change in correction.changes},
            )
            iteration = IterationResult(
                iteration_index=idx,
                correction_result=correction,
                risk_summary=risk_summary,
            )
            iterations.append(iteration)

            no_changes = len(correction.changes) == 0
            low_residual_risk = risk_summary.document_risk_score <= self.early_stop_risk_threshold
            if no_changes or low_residual_risk:
                break
            tokens = correction.corrected_tokens

        return iterations
