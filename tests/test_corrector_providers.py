from correction.factory import build_corrector


def test_build_corrector_mock_provider() -> None:
    cfg = {
        "provider": {
            "name": "mock",
            "model": "unused",
            "fallback_to_mock_on_error": True,
        }
    }
    corrector = build_corrector(cfg)
    result = corrector.correct_tokens(["qu1ck"])
    assert result.corrected_tokens == ["quick"]


def test_gemini_falls_back_to_mock_without_key() -> None:
    cfg = {
        "provider": {
            "name": "gemini",
            "model": "gemini-2.0-flash",
            "timeout_seconds": 0.1,
            "fallback_to_mock_on_error": True,
        }
    }
    corrector = build_corrector(cfg)
    result = corrector.correct_tokens(["br0wn"])
    assert result.corrected_tokens == ["brown"]
