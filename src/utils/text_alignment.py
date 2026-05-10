"""Text alignment utilities."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def levenshtein_distance(a: Sequence[T], b: Sequence[T]) -> int:
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            insertions = previous[j] + 1
            deletions = current[j - 1] + 1
            substitutions = previous[j - 1] + (0 if ca == cb else 1)
            current.append(min(insertions, deletions, substitutions))
        previous = current
    return previous[-1]
