"""Run the full sample OCR refinement pipeline and save artifacts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline.run_pipeline import run_pipeline


if __name__ == "__main__":
    result = run_pipeline(project_root=ROOT)
    print("Sample pipeline finished.")
    for key, value in result.items():
        print(f"- {key}: {value}")
