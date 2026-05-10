"""Gemini-backed OCR correction implementation."""

from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from correction.base import BaseCorrector, CorrectionResult
from correction.mock_corrector import MockLLMCorrector
from correction.provider_common import LLMProviderError
from correction.provider_parsing import build_result_from_text, build_prompt

logger = logging.getLogger(__name__)


class GeminiCorrector(BaseCorrector):
    """Gemini API corrector using generateContent."""

    def __init__(
        self,
        model: str,
        timeout_seconds: float,
        temperature: float,
        fallback_to_mock_on_error: bool,
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self.fallback_to_mock_on_error = fallback_to_mock_on_error
        self.mock_fallback = MockLLMCorrector()

    def correct_tokens(self, tokens: list[str]) -> CorrectionResult:
        try:
            corrected_text = self._call_gemini(tokens)
            return build_result_from_text(tokens, corrected_text, "gemini_inference")
        except Exception as exc:  # noqa: BLE001
            if self.fallback_to_mock_on_error:
                logger.warning("Gemini inference failed; falling back to mock corrector: %s", exc)
                return self.mock_fallback.correct_tokens(tokens)
            raise LLMProviderError(f"Gemini inference failed: {exc}") from exc

    def _call_gemini(self, tokens: list[str]) -> str:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise LLMProviderError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY)")

        prompt = build_prompt(tokens)
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": self.temperature},
        }
        body = json.dumps(payload).encode("utf-8")
        req = Request(endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")

        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:  # noqa: S310
                response_data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise LLMProviderError(f"Gemini request failed: {exc}") from exc

        parts = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise LLMProviderError("Gemini returned an empty response")
        return text
