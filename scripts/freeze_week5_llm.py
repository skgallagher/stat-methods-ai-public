"""Freeze the Week 5 LLM comparison data from the Open LLM Leaderboard.

The release records, for eight open-weight chat models, whether each model got
each BIG-Bench Hard (BBH) question right in the Open LLM Leaderboard v2 run.
All eight models answered the same 5,761 questions in 24 tasks, so any two
models can be compared question by question.

The per-question files are in the leaderboard's "details" datasets on Hugging
Face. Those datasets are gated: log in with `huggingface-cli login` and accept
each dataset's terms on its web page before downloading.

Usage:
    python scripts/freeze_week5_llm.py --source-dir SOURCE --download   # first time
    python scripts/freeze_week5_llm.py --source-dir SOURCE              # rebuild
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "course" / "llm_bbh"

# column name, Hugging Face model, details-dataset folder, developer,
# parameters in billions (safetensors total from the model page, Oct 2026),
# license (from the model page, Oct 2026)
MODELS = [
    ("llama31_70b", "meta-llama/Llama-3.1-70B-Instruct", "meta-llama__Llama-3.1-70B-Instruct", "Meta", 70.55, "Llama 3.1 Community License"),
    ("gemma2_9b", "google/gemma-2-9b-it", "google__gemma-2-9b-it", "Google", 9.24, "Gemma Terms of Use"),
    ("llama31_8b", "meta-llama/Llama-3.1-8B-Instruct", "meta-llama__Llama-3.1-8B-Instruct", "Meta", 8.03, "Llama 3.1 Community License"),
    ("qwen25_7b", "Qwen/Qwen2.5-7B-Instruct", "Qwen__Qwen2.5-7B-Instruct", "Alibaba (Qwen)", 7.62, "Apache 2.0"),
    ("mistral_7b", "mistralai/Mistral-7B-Instruct-v0.3", "mistralai__Mistral-7B-Instruct-v0.3", "Mistral AI", 7.25, "Apache 2.0"),
    ("phi35_mini", "microsoft/Phi-3.5-mini-instruct", "microsoft__Phi-3.5-mini-instruct", "Microsoft", 3.82, "MIT"),
    ("llama32_3b", "meta-llama/Llama-3.2-3B-Instruct", "meta-llama__Llama-3.2-3B-Instruct", "Meta", 3.21, "Llama 3.2 Community License"),
    ("gemma2_2b", "google/gemma-2-2b-it", "gg-hf__gemma-2-2b-it", "Google", 2.61, "Gemma Terms of Use"),
]


def details_repo(folder: str) -> str:
    return f"open-llm-leaderboard/{folder}-details"


def download(source_dir: Path) -> None:
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    for _, _, folder, _, _, _ in MODELS:
        repo = details_repo(folder)
        # Most models' files end in .jsonl; Mistral's end in .json but are also one record per line.
        files = [f for f in api.list_repo_files(repo, repo_type="dataset")
                 if "samples_leaderboard_bbh_" in f and f.endswith((".jsonl", ".json"))]
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        download(args.source_dir)

    questions = {}
    correct = {}
    model_rows = []
    source_digest = {}
    for column, hf_model, folder, developer, params, license_name in MODELS:
        paths = sorted((args.source_dir / folder).glob("samples_leaderboard_bbh_*.json*"))
        assert len(paths) == 24, f"{folder}: expected 24 BBH task files, found {len(paths)}"
        run_dates = {p.name.rsplit("_", 1)[1][:10] for p in paths}
        assert len(run_dates) == 1, f"{folder}: more than one run date {run_dates}"
        digest = hashlib.sha256()
        for path in paths:
            digest.update(path.read_bytes())
            task = task_name(path)
            for record in read_jsonl(path):
                key = (task, int(record["doc_id"]))
                item = {"doc_hash": record["doc_hash"], "input": record["doc"]["input"],
                        "target": record["doc"]["target"], "n_options": len(record["filtered_resps"])}
                if key in questions:
                    assert questions[key] == item, f"{key}: question differs across models"
                else:
                    questions[key] = item
                correct.setdefault(key, {})[column] = int(record["acc_norm"])
        source_digest[folder] = digest.hexdigest()
        model_rows.append({"column": column, "model": hf_model, "developer": developer,
                           "parameters_billion": params, "memory_gb_16bit": round(2 * params, 1),
                           "license": license_name, "leaderboard_run_date": run_dates.pop(), "details_dataset": details_repo(folder)})

    keys = sorted(questions)
    columns = [m[0] for m in MODELS]
    assert all(len(correct[k]) == len(columns) for k in keys), "some question is missing a model"

    question_rows = []
    correct_rows = []
    for task, doc_id in keys:
        question_id = f"{task}_{doc_id:03d}"
        item = questions[(task, doc_id)]
        question_rows.append({"question_id": question_id, "task": task, "n_options": item["n_options"],
                              "target": item["target"], "input": item["input"]})
        row = {"question_id": question_id, "task": task}
        for column in columns:
            row[column] = correct[(task, doc_id)][column]
        correct_rows.append(row)

    question_table = pd.DataFrame(question_rows)
    correct_table = pd.DataFrame(correct_rows)
    model_table = pd.DataFrame(model_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    question_table.to_csv(OUT / "questions.csv", index=False)
    correct_table.to_csv(OUT / "correct.csv", index=False)
    model_table.to_csv(OUT / "models.csv", index=False)

    per_task = correct_table.groupby("task")[columns].mean()
    summary = {
        "source": "Open LLM Leaderboard v2 details datasets (Hugging Face), BBH task files",
        "source_sha256_by_model": source_digest,
        "questions": len(correct_table),
        "tasks": int(correct_table["task"].nunique()),
        "chance_accuracy": round(float((1 / question_table["n_options"]).mean()), 4),
        "accuracy": {c: round(float(correct_table[c].mean()), 4) for c in columns},
        "task_range_phi35_minus_qwen25": [round(float((per_task["phi35_mini"] - per_task["qwen25_7b"]).min()), 4),
                                          round(float((per_task["phi35_mini"] - per_task["qwen25_7b"]).max()), 4)],
    }
    (OUT / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "source_sha256_by_model"}, indent=2))


if __name__ == "__main__":
    main()
