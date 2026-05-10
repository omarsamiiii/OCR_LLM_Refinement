from correction.mock_corrector import MockLLMCorrector


def test_corrector_fixes_common_confusions() -> None:
    corrector = MockLLMCorrector()
    result = corrector.correct_tokens(["The", "qu1ck", "br0wn", "0ver", "d0g."])

    assert result.corrected_tokens == ["The", "quick", "brown", "over", "dog."]
    assert len(result.changes) >= 4
