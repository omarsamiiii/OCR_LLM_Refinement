from pathlib import Path

from ocr.engine import MockJsonOCREngine


def test_mock_ocr_loads_sample() -> None:
    root = Path(__file__).resolve().parents[1]
    engine = MockJsonOCREngine(default_confidence=0.7)
    doc = engine.process(str(root / "data" / "samples" / "sample_ocr_input.json"))

    assert doc.document_id == "doc-001"
    assert "qu1ck" in doc.raw_text
    assert len(doc.tokens) > 5
    assert doc.tokens[1].confidence is not None
