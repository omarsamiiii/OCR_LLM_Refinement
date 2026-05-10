"""Ollama-backed OCR correction implementation."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from correction.base import BaseCorrector, CorrectionResult
from correction.mock_corrector import MockLLMCorrector
from correction.provider_common import LLMProviderError
from correction.provider_parsing import build_result_from_text, build_prompt

logger = logging.getLogger(__name__)


class OllamaCorrector(BaseCorrector):
    """Ollama local API corrector."""

    def __init__(
        self,
        model: str,
        timeout_seconds: float,
        temperature: float,
        fallback_to_mock_on_error: bool,
        endpoint: str = "http://localhost:11434/api/generate",
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self.endpoint = endpoint
        self.fallback_to_mock_on_error = fallback_to_mock_on_error
        self.mock_fallback = MockLLMCorrector()

    def correct_tokens(self, tokens: list[str]) -> CorrectionResult:
        try:
            corrected_text = self._call_ollama(tokens)
            return build_result_from_text(tokens, corrected_text, "ollama_inference")
        except Exception as exc:  # noqa: BLE001
            if self.fallback_to_mock_on_error:
                logger.warning("Ollama inference failed; falling back to mock corrector: %s", exc)
                return self.mock_fallback.correct_tokens(tokens)
            raise LLMProviderError(f"Ollama inference failed: {exc}") from exc

    def _call_ollama(self, tokens: list[str]) -> str:
        prompt = build_prompt(tokens)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        body = json.dumps(payload).encode("utf-8")
        req = Request(self.endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")

        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:  # noqa: S310
                response_data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise LLMProviderError(f"Ollama request failed: {exc}") from exc

        text = response_data.get("response", "").strip()
        if not text:
            raise LLMProviderError("Ollama returned an empty response")
        return text
