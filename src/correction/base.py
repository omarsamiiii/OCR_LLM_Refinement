"""Shared correction interfaces and result models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class TokenChange:
    """Represents one token-level correction."""

    token_index: int
    original: str
    corrected: str
    reason: str


@dataclass(slots=True)
class CorrectionResult:
    """Output of a correction pass."""

    corrected_text: str
    corrected_tokens: list[str]
    changes: list[TokenChange]


class BaseCorrector(ABC):
    """Abstract interface for token-level OCR correctors."""

    @abstractmethod
    def correct_tokens(self, tokens: list[str]) -> CorrectionResult:
        """Correct OCR tokens and return structured correction output."""
