"""Freeze the Week 6 confidence data: each model's probability for its own answer.

For three of the Week 5 models, this records one number per BIG-Bench Hard
question: the model's probability for the answer option it found most likely,
after rescaling the option probabilities to add to 1. It also records whether
that option was right.

The source is the same Open LLM Leaderboard "details" run that Week 5 froze
(checked against the Week 5 source hashes). Those datasets are gated: log in
with `huggingface-cli login` and accept each dataset's terms before
downloading. As in Week 5, the release does not redistribute option scores or
prompts, only the derived confidence and right/wrong outcome.

Usage:
    python scripts/freeze_week6_llm_confidence.py --source-dir SOURCE --download   # first time
    python scripts/freeze_week6_llm_confidence.py --source-dir SOURCE              # rebuild
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import argparse

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "course" / "llm_bbh"

# column name in correct.csv, details-dataset folder, run timestamp frozen in Week 5
MODELS = [
    ("qwen25_7b", "Qwen__Qwen2.5-7B-Instruct", "2024-09-19T16-21-01.446061"),
    ("llama31_8b", "meta-llama__Llama-3.1-8B-Instruct", "2025-02-06T09-49-35.437423"),
    ("gemma2_2b", "gg-hf__gemma-2-2b-it", "2024-07-29T16-25-50.870458"),
]

# Gemma-2-2B's details dataset has moved to google__gemma-2-2b-it-details since
# Week 5 was frozen; its files still sit in a gg-hf__gemma-2-2b-it folder.
REPO_NAMES = {"gg-hf__gemma-2-2b-it": "google__gemma-2-2b-it"}


def details_repo(folder: str) -> str:
    return f"open-llm-leaderboard/{REPO_NAMES.get(folder, folder)}-details"


def download(source_dir: Path) -> None:
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    for _, folder, stamp in MODELS:
        repo = details_repo(folder)
        files = [f for f in api.list_repo_files(repo, repo_type="dataset")
                 if "samples_leaderboard_bbh_" in f and stamp in f]
        for name in files:
            hf_hub_download(repo, name, repo_type="dataset", local_dir=source_dir)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as stream:
        for line in stream:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def task_name(path: Path) -> str:
    return path.name.split("samples_leaderboard_bbh_")[1].rsplit("_20", 1)[0]


def as_object(value):
    # Some details files store nested fields as Python-literal strings.
    return ast.literal_eval(value) if isinstance(value, str) else value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        download(args.source_dir)

    week5_summary = json.loads((OUT / "release_summary.json").read_text())
    week5_correct = pd.read_csv(OUT / "correct.csv").set_index("question_id")
    questions = pd.read_csv(OUT / "questions.csv").set_index("question_id")

    table = questions[["task", "n_options"]].copy()
    checks = {}
    for column, folder, stamp in MODELS:
        paths = sorted(p for p in (args.source_dir / folder).glob("samples_leaderboard_bbh_*.json*") if stamp in p.name)
        assert len(paths) == 24, f"{folder}: expected 24 task files for {stamp}, found {len(paths)}"
        digest = hashlib.sha256()
        for path in paths:
            digest.update(path.read_bytes())
        assert digest.hexdigest() == week5_summary["source_sha256_by_model"][folder], f"{folder}: not the Week 5 run"

        confidence = {}
        right = {}
        for path in paths:
            task = task_name(path)
            for record in read_jsonl(path):
                question_id = f"{task}_{int(record['doc_id']):03d}"
                arguments = as_object(record["arguments"])
                options = [arguments[f"gen_args_{k}"]["arg_1"].strip() for k in range(len(arguments))]
                scores = np.array([float(as_object(r)[0]) for r in as_object(record["filtered_resps"])])
                assert len(options) == len(scores) == questions.loc[question_id, "n_options"]
                probs = np.exp(scores - scores.max())
                probs = probs / probs.sum()
                chosen = int(np.argmax(probs))
                confidence[question_id] = round(float(probs[chosen]), 4)
                right[question_id] = int(options[chosen] == str(record["target"]).strip())
        table[f"{column}_confidence"] = pd.Series(confidence)
        table[f"{column}_right"] = pd.Series(right)
        assert table[f"{column}_confidence"].notna().all()
        same_as_week5 = (table[f"{column}_right"] == week5_correct[column]).mean()
        checks[column] = {
            "accuracy": round(float(table[f"{column}_right"].mean()), 4),
            "mean_confidence": round(float(table[f"{column}_confidence"].mean()), 4),
            "agreement_with_week5_right_wrong": round(float(same_as_week5), 4),
        }

    table = table.reset_index()
    table.to_csv(OUT / "confidence.csv", index=False)
    summary = {
        "source": "Open LLM Leaderboard v2 details datasets (Hugging Face), the same BBH runs frozen in Week 5",
        "rule": "answer = option with the highest probability, after rescaling the option probabilities to add to 1",
        "questions": len(table),
        "models": checks,
    }
    (OUT / "confidence_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
