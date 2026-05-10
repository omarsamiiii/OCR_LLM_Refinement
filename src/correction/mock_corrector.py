"""Mock deterministic LLM-style OCR post-correction module."""

from __future__ import annotations

import re

from correction.base import BaseCorrector, CorrectionResult, TokenChange


class MockLLMCorrector(BaseCorrector):
    """Simple heuristic corrector for common OCR confusions."""

    KNOWN_OVERRIDES: dict[str, str] = {
        "qu1ck": "quick",
        "br0wn": "brown",
        "0ver": "over",
        "d0g": "dog",
        "sunr1se": "sunrise",
        "m0rning": "morning",
        "qu1et": "quiet",
        "rnarket": "market",
    }

    def correct_tokens(self, tokens: list[str]) -> CorrectionResult:
        corrected_tokens: list[str] = []
        changes: list[TokenChange] = []

        for idx, token in enumerate(tokens):
            corrected, reason = self._correct_one_token(token)
            corrected_tokens.append(corrected)
            if corrected != token:
                changes.append(
                    TokenChange(
                        token_index=idx,
                        original=token,
                        corrected=corrected,
                        reason=reason,
                    )
                )

        return CorrectionResult(
            corrected_text=" ".join(corrected_tokens),
            corrected_tokens=corrected_tokens,
            changes=changes,
        )

    def _correct_one_token(self, token: str) -> tuple[str, str]:
        prefix, core, suffix = self._split_token(token)
        lowered = core.lower()

        if lowered in self.KNOWN_OVERRIDES:
            corrected = self._preserve_case(core, self.KNOWN_OVERRIDES[lowered])
            return f"{prefix}{corrected}{suffix}", "known_confusion_override"

        updated = core
        reason_parts: list[str] = []

        if re.search(r"[A-Za-z]0[A-Za-z]", updated):
            updated = re.sub(r"0", "o", updated)
            reason_parts.append("digit_zero_in_word")

        if re.search(r"[A-Za-z]1[A-Za-z]", updated):
            updated = re.sub(r"1", "i", updated)
            reason_parts.append("digit_one_in_word")

        if "rn" in updated.lower():
            maybe = re.sub(r"rn", "m", updated, flags=re.IGNORECASE)
            if maybe != updated and len(updated) > 3:
                updated = maybe
                reason_parts.append("rn_to_m_pattern")

        if re.search(r"[A-Za-z]+\d+[A-Za-z]+", updated):
            updated = re.sub(r"\d", "", updated)
            reason_parts.append("remove_embedded_digit")

        if not reason_parts:
            return token, "no_change"

        corrected = f"{prefix}{updated}{suffix}"
        return corrected, "+".join(reason_parts)

    @staticmethod
    def _split_token(token: str) -> tuple[str, str, str]:
        match = re.match(r"^(\W*)([\w']+)(\W*)$", token)
        if not match:
            return "", token, ""
        return match.group(1), match.group(2), match.group(3)

    @staticmethod
    def _preserve_case(original: str, replacement: str) -> str:
        if original.isupper():
            return replacement.upper()
        if original[:1].isupper():
            return replacement.capitalize()
        return replacement
