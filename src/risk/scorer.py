"""Residual risk scoring module."""

from __future__ import annotations

import re
from dataclasses import dataclass

from risk.calibrator import RiskCalibrator


@dataclass(slots=True)
class RiskScore:
    """Token-level risk score."""

    token: str
    score: float
    level: str


@dataclass(slots=True)
class DocumentRiskSummary:
    """Document-level risk summary and token details."""

    token_risks: list[RiskScore]
    document_risk_score: float


class RiskScorer:
    """Heuristic residual risk scorer."""

    def __init__(
        self,
        medium_threshold: float,
        high_threshold: float,
        calibrator: RiskCalibrator,
    ) -> None:
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold
        self.calibrator = calibrator

    def score(
        self,
        tokens: list[str],
        confidences: list[float | None],
        changed_indices: set[int],
    ) -> DocumentRiskSummary:
        token_risks: list[RiskScore] = []

        for idx, token in enumerate(tokens):
            confidence = confidences[idx] if idx < len(confidences) else None
            token_score = self._score_token(
                token=token,
                confidence=confidence,
                changed=idx in changed_indices,
            )
            calibrated = self.calibrator.calibrate(token_score)
            token_risks.append(
                RiskScore(
                    token=token,
                    score=calibrated,
                    level=self._risk_level(calibrated),
                )
            )

        avg_score = sum(t.score for t in token_risks) / len(token_risks) if token_risks else 0.0
        return DocumentRiskSummary(token_risks=token_risks, document_risk_score=avg_score)

    def _score_token(self, token: str, confidence: float | None, changed: bool) -> float:
        score = 0.0

        if confidence is not None:
            score += 1.0 - max(0.0, min(1.0, confidence))
        else:
            score += 0.2

        if changed:
            score += 0.2

        if re.search(r"[A-Za-z]\d|\d[A-Za-z]", token):
            score += 0.35
        if re.search(r"[!?.,;:]{2,}", token):
            score += 0.2
        if re.search(r"(.)\1\1", token):
            score += 0.2
        if len(token) > 20:
            score += 0.1

        return min(score, 1.0)

    def _risk_level(self, score: float) -> str:
        if score >= self.high_threshold:
            return "high"
        if score >= self.medium_threshold:
            return "medium"
        return "low"
