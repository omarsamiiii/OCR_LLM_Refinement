"""Shared prompt and response parsing helpers for LLM providers."""

from __future__ import annotations

from correction.base import CorrectionResult, TokenChange


def build_prompt(tokens: list[str]) -> str:
    text = " ".join(tokens)
    return (
        "You are an OCR correction assistant. Correct OCR mistakes while preserving meaning. "
        "Return only the corrected plain text and nothing else.\n"
        f"Input OCR text:\n{text}"
    )


def build_result_from_text(original_tokens: list[str], corrected_text: str, reason: str) -> CorrectionResult:
    corrected_tokens = corrected_text.split()
    changes: list[TokenChange] = []

    max_len = max(len(original_tokens), len(corrected_tokens))
    for idx in range(max_len):
        original = original_tokens[idx] if idx < len(original_tokens) else ""
        corrected = corrected_tokens[idx] if idx < len(corrected_tokens) else ""
        if original != corrected:
            changes.append(
                TokenChange(
                    token_index=idx,
                    original=original,
                    corrected=corrected,
                    reason=reason,
                )
            )

    return CorrectionResult(
        corrected_text=" ".join(corrected_tokens),
        corrected_tokens=corrected_tokens,
        changes=changes,
    )
