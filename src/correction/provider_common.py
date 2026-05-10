"""Shared provider utilities and exceptions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProviderSettings:
    """Provider settings loaded from config."""

    provider: str
    model: str
    timeout_seconds: float = 20.0
    temperature: float = 0.0
    fallback_to_mock_on_error: bool = True


class LLMProviderError(RuntimeError):
    """Raised when provider inference fails and no fallback is enabled."""
