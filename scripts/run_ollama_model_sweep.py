"""Run pipeline across multiple Ollama models and save a comparison report."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline.run_pipeline import run_pipeline
from utils.io import read_json, read_yaml, write_json

MODELS = [
    "llama3.1:8b",
    "gemma3:4b",
    "qwen2.5-coder:7b",
    "qwen3:8b",
    "deepseek-r1:8b",
]


def _sanitize_model_name(name: str) -> str:
    return name.replace(":", "-").replace("/", "-")


def _ollama_available_models(endpoint: str) -> set[str]:
    tags_endpoint = endpoint.replace("/api/generate", "/api/tags")
    req = Request(tags_endpoint, method="GET")
    with urlopen(req, timeout=5) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    return {item.get("name", "") for item in payload.get("models", [])}


if __name__ == "__main__":
    llm_cfg = read_yaml(ROOT / "configs" / "llm.yaml")
    provider_cfg = llm_cfg["correction"]["provider"]
    if provider_cfg.get("name") != "ollama":
        raise ValueError("configs/llm.yaml provider.name must be 'ollama' for model sweep")

    endpoint = str(provider_cfg.get("endpoint", "http://localhost:11434/api/generate"))

    try:
        available = _ollama_available_models(endpoint)
    except URLError as exc:
        raise RuntimeError(
            f"Could not reach Ollama server at {endpoint}. Start it with 'ollama serve'."
        ) from exc

    summary: list[dict[str, object]] = []

    for model in MODELS:
        model_tagged = model if ":" in model else f"{model}:latest"
        if model_tagged not in available and model not in available:
            summary.append({
                "model": model,
                "status": "skipped_not_downloaded",
                "runtime_seconds": None,
                "metrics": None,
            })
            continue

        provider_cfg["model"] = model
        run_label = f"ollama_{_sanitize_model_name(model)}"

        start = time.perf_counter()
        try:
            result = run_pipeline(project_root=ROOT, run_label=run_label)
            metrics = read_json(Path(result["metrics_path"]))
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            metrics = {"error": str(exc)}
            status = "failed"
            result = {"metrics_path": ""}
        runtime = round(time.perf_counter() - start, 3)

        summary.append(
            {
                "model": model,
                "status": status,
                "runtime_seconds": runtime,
                "metrics": metrics,
                "metrics_path": result.get("metrics_path", ""),
            }
        )

    out_path = ROOT / "outputs" / "metrics" / "ollama_model_sweep_summary.json"
    write_json(out_path, {"runs": summary})
    print(f"Saved model sweep summary to: {out_path}")
    for item in summary:
        print(f"- {item['model']}: {item['status']} ({item['runtime_seconds']}s)")
