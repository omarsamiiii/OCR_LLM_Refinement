"""Factory for selecting OCR correctors by provider config."""

from __future__ import annotations

from typing import Any

from correction.base import BaseCorrector
from correction.gemini_corrector import GeminiCorrector
from correction.mock_corrector import MockLLMCorrector
from correction.ollama_corrector import OllamaCorrector
from correction.provider_common import ProviderSettings


def build_corrector(correction_cfg: dict[str, Any]) -> BaseCorrector:
    """Create a corrector from config."""

    provider_cfg = correction_cfg.get("provider", {})
    settings = ProviderSettings(
        provider=str(provider_cfg.get("name", "mock")).lower(),
        model=str(provider_cfg.get("model", "")),
        timeout_seconds=float(provider_cfg.get("timeout_seconds", 20.0)),
        temperature=float(provider_cfg.get("temperature", 0.0)),
        fallback_to_mock_on_error=bool(provider_cfg.get("fallback_to_mock_on_error", True)),
    )

    if settings.provider == "mock":
        return MockLLMCorrector()
    if settings.provider == "gemini":
        return GeminiCorrector(
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
            temperature=settings.temperature,
            fallback_to_mock_on_error=settings.fallback_to_mock_on_error,
        )
    if settings.provider == "ollama":
        return OllamaCorrector(
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
            temperature=settings.temperature,
            fallback_to_mock_on_error=settings.fallback_to_mock_on_error,
            endpoint=str(provider_cfg.get("endpoint", "http://localhost:11434/api/generate")),
        )

    raise ValueError(f"Unsupported correction provider: {settings.provider}")
