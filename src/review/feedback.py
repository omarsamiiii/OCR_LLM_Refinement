"""Human feedback data hooks for future interactive review workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from utils.io import append_jsonl


@dataclass(slots=True)
class FeedbackRecord:
    """Stores one human correction or note."""

    document_id: str
    token_index: int
    original_token: str
    corrected_token: str
    reviewer_id: str
    comment: str = ""
    timestamp_utc: str = ""


class FeedbackLogger:
    """Persists human feedback records to JSONL."""

    def log(self, output_path: Path, record: FeedbackRecord) -> None:
        payload: dict[str, Any] = asdict(record)
        if not payload["timestamp_utc"]:
            payload["timestamp_utc"] = datetime.now(tz=UTC).isoformat()
        append_jsonl(output_path, payload)
