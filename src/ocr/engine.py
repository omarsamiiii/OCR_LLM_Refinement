"""Mock OCR engine implementation reading OCR output from JSON."""

from __future__ import annotations

import logging
from pathlib import Path

from ocr.base import BaseOCREngine, OCRDocument, OCRToken
from utils.io import read_json

logger = logging.getLogger(__name__)


class MockJsonOCREngine(BaseOCREngine):
    """Loads precomputed OCR content from a JSON file."""

    def __init__(self, default_confidence: float = 0.75) -> None:
        self.default_confidence = default_confidence

    def process(self, source: str) -> OCRDocument:
        input_path = Path(source)
        payload = read_json(input_path)

        document_id = payload["document_id"]
        text = payload["text"]
        token_texts: list[str] = payload.get("tokens", text.split())
        confidences: list[float] = payload.get("confidences", [])

        tokens: list[OCRToken] = []
        for idx, token in enumerate(token_texts):
            confidence = confidences[idx] if idx < len(confidences) else self.default_confidence
            tokens.append(OCRToken(text=token, confidence=confidence))

        logger.info("Loaded OCR document '%s' with %d tokens", document_id, len(tokens))
        return OCRDocument(document_id=document_id, raw_text=text, tokens=tokens)
