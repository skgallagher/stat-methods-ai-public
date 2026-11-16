"""Freeze the Week 12 data: human and GPT-4 judgments of chatbot answers from MT-Bench.

Zheng et al. (2023), "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," released
`lmsys/mt_bench_human_judgments` on Hugging Face (CC-BY-4.0). Six chat models answered 80
two-turn questions in 8 categories. For every pair of models, question, and turn (2,400
items), experts voted on which answer was better or called a tie, and GPT-4 gave a verdict.
FastChat's judging code ran GPT-4 twice at temperature 0, with the two answers in swapped
positions; the label "tie (inconsistent)" marks the items where the two orders disagreed.

This script reads the dataset's Parquet conversion at a pinned revision and writes:

- items.csv: one row per item, with the GPT-4 verdict and whether its two orders agreed;
- human_votes.csv: one row per human vote;
- questions.csv: the two turns of each question;
- answers.csv: each model's answer to each turn of each question;
- release_summary.json: sources, revisions, counts, and agreement figures.

The categories split the questions into two halves: Lab 12 uses writing, roleplay,
reasoning, and STEM; HW7 uses math, coding, extraction, and humanities.

Usage:
    python scripts/freeze_week12_mtbench.py
"""

from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "course" / "llm_judges"
REPO = "lmsys/mt_bench_human_judgments"
MAIN_REVISION = "f7d2896d2cc5d80f8b55c2bbc722613555233c25"     # last data change Jul 2023
PARQUET_REVISION = "63d601feea39fd4139ad2d03050ee5219ada5f7e"  # refs/convert/parquet
CATEGORIES = ["writing", "roleplay", "reasoning", "math", "coding", "extraction", "stem", "humanities"]
LAB_HALF = {"writing", "roleplay", "reasoning", "stem"}


def read_split(split: str) -> pd.DataFrame:
    url = (f"https://huggingface.co/datasets/{REPO}/resolve/{PARQUET_REVISION}/"
           f"default/{split}/0000.parquet")
    with urllib.request.urlopen(url) as response:
        return pd.read_parquet(io.BytesIO(response.read()))


def category(question_id: int) -> str:
    # MT-Bench numbers its questions 81-160, ten per category, in this order.
    return CATEGORIES[(question_id - 81) // 10]


def answer_text(conversation, turn: int) -> str:
    replies = [m["content"] for m in conversation if m["role"] == "assistant"]
    return replies[turn - 1]


def canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Order each pair's models alphabetically and express votes in that order."""
    df = df.copy()
    df["model_1"] = [min(a, b) for a, b in zip(df["model_a"], df["model_b"])]
    df["model_2"] = [max(a, b) for a, b in zip(df["model_a"], df["model_b"])]
    winner = np.where(df["winner"] == "model_a", df["model_a"], df["model_b"])
    df["vote"] = np.where(df["winner"].str.startswith("tie"), "tie",
                          np.where(winner == df["model_1"], "model_1", "model_2"))
    df["key"] = list(zip(df["question_id"], df["turn"], df["model_1"], df["model_2"]))
    return df


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    human = canonical(read_split("human"))
    gpt4 = canonical(read_split("gpt4_pair"))

    # Questions and answers, checked to be identical wherever they repeat.
    questions, answers = {}, {}
    for df in (human, gpt4):
        for _, row in df.iterrows():
            q = row["question_id"]
            users = [m["content"] for m in row["conversation_a"] if m["role"] == "user"]
            if q in questions and questions[q] != users:
                raise ValueError(f"question {q} differs between rows")
            questions[q] = users
            for side in ("a", "b"):
                for turn in (1, 2):
                    key = (q, row[f"model_{side}"], turn)
                    text = answer_text(row[f"conversation_{side}"], turn)
                    if key in answers and answers[key] != text:
                        raise ValueError(f"answer {key} differs between rows")
                    answers[key] = text

    # Items: every question x turn x pair of models, numbered in a fixed order.
    gpt4 = gpt4.sort_values(["question_id", "turn", "model_1", "model_2"]).reset_index(drop=True)
    if gpt4["key"].duplicated().any() or len(gpt4) != 2400:
        raise ValueError("expected exactly one GPT-4 verdict for each of 2,400 items")
    gpt4["item_id"] = [f"j{i + 1:04d}" for i in range(len(gpt4))]
    item_of = dict(zip(gpt4["key"], gpt4["item_id"]))

    human["item_id"] = human["key"].map(item_of)
    if human["item_id"].isna().any():
        raise ValueError("a human vote has no matching item")
    before = len(human)
    human = human.drop_duplicates(["item_id", "judge"], keep="first")   # one judge voted twice on one item
    dropped = before - len(human)

    items = pd.DataFrame({
        "item_id": gpt4["item_id"],
        "question_id": gpt4["question_id"],
        "category": gpt4["question_id"].map(category),
        "half": np.where(gpt4["question_id"].map(category).isin(LAB_HALF), "lab", "homework"),
        "turn": gpt4["turn"],
        "model_1": gpt4["model_1"],
        "model_2": gpt4["model_2"],
        "gpt4_verdict": gpt4["vote"],
        "gpt4_orders_agree": gpt4["winner"] != "tie (inconsistent)",
    })
    items["n_human_votes"] = items["item_id"].map(human["item_id"].value_counts()).fillna(0).astype(int)
    votes = human[["item_id", "judge", "vote"]].sort_values(["item_id", "judge"]).reset_index(drop=True)
    question_table = pd.DataFrame(
        [{"question_id": q, "category": category(q), "turn_1": u[0], "turn_2": u[1]} for q, u in sorted(questions.items())])
    answer_table = pd.DataFrame(
        [{"question_id": q, "model": m, "turn": t, "answer": text} for (q, m, t), text in sorted(answers.items())])

    items.to_csv(OUT / "items.csv", index=False)
    votes.to_csv(OUT / "human_votes.csv", index=False)
    question_table.to_csv(OUT / "questions.csv", index=False)
    answer_table.to_csv(OUT / "answers.csv", index=False)

    summary = {
        "source": f"Hugging Face dataset {REPO} (Zheng et al. 2023)",
        "source_main_revision": MAIN_REVISION,
        "source_parquet_revision": PARQUET_REVISION,
        "license": "CC-BY-4.0",
        "items": len(items),
        "questions": len(question_table),
        "answers": len(answer_table),
        "human_votes": len(votes),
        "human_votes_dropped_as_duplicates": dropped,
        "human_judges": int(votes["judge"].nunique()),
        "items_with_two_or_more_human_votes": int((items["n_human_votes"] >= 2).sum()),
        "gpt4_orders_disagree": int((~items["gpt4_orders_agree"]).sum()),
        "gpt4_judging": "GPT-4, temperature 0, run in both answer orders (FastChat llm_judge); disagreeing orders recorded as a tie",
        "halves": {"lab": sorted(LAB_HALF), "homework": sorted(set(CATEGORIES) - LAB_HALF)},
    }
    (OUT / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for path in sorted(OUT.iterdir()):
        print(f"{path.stat().st_size / 1e3:9.1f} KB  {path.name}")
    print(json.dumps({k: summary[k] for k in ("items", "human_votes", "human_votes_dropped_as_duplicates", "human_judges", "items_with_two_or_more_human_votes", "gpt4_orders_disagree")}))


if __name__ == "__main__":
    main()
