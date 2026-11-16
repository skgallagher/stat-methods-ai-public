"""Freeze the Week 11 lab data: 10,000 sampled answers per GSM8K problem from two models.

Brown et al. (2024), "Large Language Monkeys: Scaling Inference Compute with Repeated
Sampling," released the dataset `ScalingIntelligence/monkey_business` on Hugging Face
(MIT license). Its GSM8K part has 127 problems drawn at random from GSM8K's test set, each
answered 10,000 times by Llama 3 8B Instruct and by Llama 3 70B Instruct, with a five-example
prompt at temperature 0.6. Each answer is marked right if the number after "####" matches
the answer key.

This script reads only the columns it needs from the Parquet conversion at a pinned
revision (about 150 MB read for the two models), and writes a small release:

- problems.csv: one row per problem, with the question, the key, and how many of the
  10,000 answers each model got right, plus the 8B model's most common wrong answer;
- correct.npz: for each model, a 127 x 10,000 array of right (True) or wrong (False);
- answer_texts.csv: the first right and the first wrong 8B answer to each problem;
- prompts.csv: the full prompt for each problem (five worked examples, different for
  each problem, then the question);
- release_summary.json: sources, revisions, settings, counts, and accuracies.

Usage:
    python scripts/freeze_week11_gsm8k.py
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "course" / "llm_gsm8k"
REPO = "ScalingIntelligence/monkey_business"
MAIN_REVISION = "a9f8f73bcd6948a57ed922cba4e48062ef95f553"      # data files unchanged since Sep 2, 2024
PARQUET_REVISION = "5acc07474317fe5280a2618d2b6652cdb740d101"   # refs/convert/parquet, Sep 2, 2024
MODELS = {"llama3_8b": "GSM8K_Llama-3-8B-Instruct", "llama3_70b": "GSM8K_Llama-3-70B-Instruct"}
FINAL = re.compile(r"#### (\-?[0-9\.\,]+)")   # the dataset's own answer pattern


def parquet_url(config: str) -> str:
    return (f"https://huggingface.co/datasets/{REPO}/resolve/{PARQUET_REVISION}/"
            f"{config}/test/0000.parquet")


def read_columns(config: str, columns: list[str]) -> dict:
    with fsspec.open(parquet_url(config), "rb", block_size=8 * 2**20) as handle:
        table = pq.ParquetFile(handle).read(columns=columns)
    return {name: table.column(name).to_pylist() for name in columns}


def final_answer(text: str) -> str | None:
    match = FINAL.search(text)
    return match.group(1).replace(",", "").rstrip(".") if match else None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    small = read_columns(MODELS["llama3_8b"], ["orig_dset_idx", "question", "gt_answer", "prompt", "samples", "is_corrects"])
    large = read_columns(MODELS["llama3_70b"], ["orig_dset_idx", "question", "is_corrects"])
    if small["orig_dset_idx"] != large["orig_dset_idx"] or small["question"] != large["question"]:
        raise ValueError("The two models' problems are not in the same order.")

    correct = {
        "llama3_8b": np.array(small["is_corrects"], dtype=bool),
        "llama3_70b": np.array(large["is_corrects"], dtype=bool),
    }
    n_problems, n_answers = correct["llama3_8b"].shape
    if correct["llama3_70b"].shape != (n_problems, n_answers) or n_answers != 10_000:
        raise ValueError("Unexpected array shapes.")

    # Problems are numbered in the dataset's order, which is a random draw from the test set.
    problem_ids = [f"g{i + 1:03d}" for i in range(n_problems)]
    rows, texts = [], []
    for i, pid in enumerate(problem_ids):
        samples = small["samples"][i]
        flags = small["is_corrects"][i]
        if len(samples) != n_answers:
            raise ValueError(f"{pid}: expected {n_answers} answers, found {len(samples)}")
        finals = [final_answer(s) for s in samples]
        wrong_finals = collections.Counter(f for f, ok in zip(finals, flags) if not ok)
        common_wrong, common_wrong_count = (wrong_finals.most_common(1) or [(None, 0)])[0]
        rows.append({
            "problem_id": pid,
            "gsm8k_test_index": small["orig_dset_idx"][i],
            "question": small["question"][i],
            "answer": small["gt_answer"][i].split("####")[-1].strip().replace(",", ""),
            "solution": small["gt_answer"][i],
            "right_8b": int(correct["llama3_8b"][i].sum()),
            "right_70b": int(correct["llama3_70b"][i].sum()),
            "most_common_wrong_8b": common_wrong if common_wrong is not None else "",
            "most_common_wrong_count_8b": common_wrong_count,
            "no_final_answer_8b": sum(f is None for f in finals),
        })
        for wanted in (True, False):
            k = next((k for k, ok in enumerate(flags) if ok is wanted), None)
            if k is not None:
                texts.append({"problem_id": pid, "model": "llama3_8b", "answer_index": k,
                              "correct": wanted, "final_answer": finals[k] or "", "text": samples[k].strip()})

    problems = pd.DataFrame(rows)
    problems.to_csv(OUT / "problems.csv", index=False)
    pd.DataFrame(texts).to_csv(OUT / "answer_texts.csv", index=False)
    np.savez_compressed(OUT / "correct.npz", **correct)
    pd.DataFrame({"problem_id": problem_ids, "prompt": small["prompt"]}).to_csv(OUT / "prompts.csv", index=False)

    p8 = correct["llama3_8b"].mean(axis=1)
    p70 = correct["llama3_70b"].mean(axis=1)
    summary = {
        "source": f"Hugging Face dataset {REPO} (Brown et al. 2024, Large Language Monkeys)",
        "source_main_revision": MAIN_REVISION,
        "source_parquet_revision": PARQUET_REVISION,
        "license": "MIT (dataset); GSM8K is MIT (Cobbe et al. 2021); answers are Llama 3 outputs under the Meta Llama 3 Community License",
        "models": {"llama3_8b": "meta-llama/Meta-Llama-3-8B-Instruct", "llama3_70b": "meta-llama/Meta-Llama-3-70B-Instruct"},
        "sampling": {"temperature": 0.6, "few_shot_examples": "5, different for each problem", "max_new_tokens": 512, "answers_per_problem": n_answers},
        "correctness": "the number after '####' in the answer equals the one in the answer key (string match)",
        "problems": n_problems,
        "gsm8k_test_problems": 1319,
        "accuracy": {"llama3_8b": round(float(p8.mean()), 4), "llama3_70b": round(float(p70.mean()), 4)},
        "between_problem_variance_8b": round(float(p8.var()), 4),
        "within_problem_variance_8b": round(float((p8 * (1 - p8)).mean()), 4),
        "correct_npz_sha256": sha256(OUT / "correct.npz"),
    }
    (OUT / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for path in sorted(OUT.iterdir()):
        print(f"{path.stat().st_size / 1e3:9.1f} KB  {path.name}")
    print(json.dumps(summary["accuracy"]))


if __name__ == "__main__":
    main()
