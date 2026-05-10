"""Base OCR data models and interfaces."""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class OCRToken:
    """Represents a token produced by OCR."""

    text: str
    confidence: Optional[float] = None


@dataclass(slots=True)
class OCRDocument:
    """Represents OCR output for one document."""

    document_id: str
    raw_text: str
    tokens: list[OCRToken]


class BaseOCREngine:
    """Abstract interface for OCR engines."""

    def process(self, source: str) -> OCRDocument:
        raise NotImplementedError
