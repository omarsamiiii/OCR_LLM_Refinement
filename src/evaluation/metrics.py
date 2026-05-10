"""Evaluation metrics for OCR correction quality."""

from __future__ import annotations

from dataclasses import dataclass

from utils.text_alignment import levenshtein_distance


@dataclass(slots=True)
class EvaluationMetrics:
    """Core evaluation metrics."""

    character_error_rate: float
    word_error_rate: float
    token_error_precision: float
    token_error_recall: float
    token_error_f1: float


def character_error_rate(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein_distance(reference, hypothesis) / len(reference)


def word_error_rate(reference: str, hypothesis: str) -> float:
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    return levenshtein_distance(ref_words, hyp_words) / len(ref_words)


def token_error_prf(reference: str, raw: str, corrected: str) -> tuple[float, float, float]:
    ref_tokens = reference.split()
    raw_tokens = raw.split()
    cor_tokens = corrected.split()
    n = min(len(ref_tokens), len(raw_tokens), len(cor_tokens))

    predicted_error = 0
    true_error = 0
    true_positive = 0

    for i in range(n):
        raw_is_error = raw_tokens[i] != ref_tokens[i]
        cor_changed = cor_tokens[i] != raw_tokens[i]
        cor_fixed = cor_tokens[i] == ref_tokens[i]

        if cor_changed:
            predicted_error += 1
        if raw_is_error:
            true_error += 1
        if cor_changed and cor_fixed and raw_is_error:
            true_positive += 1

    precision = true_positive / predicted_error if predicted_error else 0.0
    recall = true_positive / true_error if true_error else 0.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def evaluate(reference: str, raw: str, corrected: str) -> EvaluationMetrics:
    cer = character_error_rate(reference, corrected)
    wer = word_error_rate(reference, corrected)
    precision, recall, f1 = token_error_prf(reference, raw, corrected)
    return EvaluationMetrics(
        character_error_rate=cer,
        word_error_rate=wer,
        token_error_precision=precision,
        token_error_recall=recall,
        token_error_f1=f1,
    )
