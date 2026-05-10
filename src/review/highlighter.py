"""Generate review-ready HTML artifacts with risk highlighting."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

from risk.scorer import RiskScore


@dataclass(slots=True)
class ReviewArtifact:
    """Represents produced review artifact."""

    document_id: str
    html_path: Path


class ReviewHighlighter:
    """Writes HTML with token risk highlights."""

    COLOR_BY_LEVEL = {
        "low": "#1f2937",
        "medium": "#1d4ed8",
        "high": "#b91c1c",
    }

    def write_html(self, document_id: str, token_risks: list[RiskScore], output_path: Path) -> ReviewArtifact:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        token_html = " ".join(
            f"<span style='color:{self.COLOR_BY_LEVEL.get(item.level, '#111827')}' title='risk={item.score:.2f}|{item.level}'>"
            f"{escape(item.token)}</span>"
            for item in token_risks
        )

        html = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Review Highlight - {escape(document_id)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
    .legend {{ margin-bottom: 1rem; padding: 0.75rem; border: 1px solid #ddd; border-radius: 8px; }}
    .label {{ font-weight: 700; }}
    .token-block {{ padding: 1rem; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }}
  </style>
</head>
<body>
  <h1>Risk-Aware OCR Review</h1>
  <p><strong>Document:</strong> {escape(document_id)}</p>
  <div class='legend'>
    <span class='label'>Legend:</span>
    <span style='color:#1f2937'>Low risk</span> |
    <span style='color:#1d4ed8'>Medium risk</span> |
    <span style='color:#b91c1c'>High risk</span>
  </div>
  <div class='token-block'>{token_html}</div>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        return ReviewArtifact(document_id=document_id, html_path=output_path)
