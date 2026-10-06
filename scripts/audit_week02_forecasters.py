"""Run the proposed Week 2 sentiment forecasters on difficult DynaSent cases.

This is an instructor-side release audit. It reads official DynaSent JSONL files,
runs two pinned public Hugging Face checkpoints, and writes a candidate table for
selecting a small fixed Problem 3 subset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from transformers import pipeline


LABELS = ["negative", "neutral", "positive"]
MODELS = {
    "cardiff": (
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7",
    ),
    "distilbert": (
        "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        "cf991100d706c13c0a080c097134c05b7f436c45",
    ),
}
SELECTED_IDS = [
    "r1-0101399",
    "r2-0019264",
    "r2-0019273",
    "r1-0100076",
    "r2-0019953",
    "r1-0099714",
    "r1-0099211",
    "r2-0019787",
    "r2-0019433",
    "r1-0099908",
]


def read_dynasent(paths: list[Path]) -> pd.DataFrame:
    rows: list[dict] = []
    for path in paths:
        round_number = 1 if "round01" in path.name else 2
        with path.open() as stream:
            for line in stream:
                item = json.loads(line)
                distribution = item["label_distribution"]
                counts = {label: len(distribution.get(label, [])) for label in LABELS}
                mixed = len(distribution.get("mixed", []))
                total = sum(counts.values())
                if mixed or total != 5 or max(counts.values()) not in {3, 4}:
                    continue
                ordered = sorted(counts.values(), reverse=True)
                rows.append(
                    {
                        "item_id": item["text_id"],
                        "sentence": item["sentence"],
                        "collection_round": round_number,
                        **{f"{label}_votes": counts[label] for label in LABELS},
                        **{f"q_{label}": counts[label] / total for label in LABELS},
                        "majority_label": max(counts, key=counts.get),
                        "vote_pattern": f"{ordered[0]}-{ordered[1]}",
                    }
                )
    frame = pd.DataFrame(rows).drop_duplicates("item_id")
    return frame.loc[frame["sentence"].str.len().between(15, 280)].reset_index(drop=True)


def run_model(frame: pd.DataFrame, short_name: str, batch_size: int) -> pd.DataFrame:
    model_id, revision = MODELS[short_name]
    classifier = pipeline(
        "text-classification",
        model=model_id,
        revision=revision,
        top_k=None,
        device=-1,
    )
    raw = classifier(
        frame["sentence"].tolist(),
        truncation=True,
        batch_size=batch_size,
    )
    records = []
    for result in raw:
        scores = {entry["label"].lower(): float(entry["score"]) for entry in result}
        missing = set(LABELS) - set(scores)
        if missing:
            raise ValueError(f"{model_id} did not return expected labels: {missing}")
        records.append(
            {
                **{f"{short_name}_p_{label}": scores[label] for label in LABELS},
                f"{short_name}_label": max(LABELS, key=scores.get),
                f"{short_name}_confidence": max(scores.values()),
            }
        )
    return pd.DataFrame(records)


def add_audit_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    target = result[[f"q_{label}" for label in LABELS]].to_numpy()
    for short_name in MODELS:
        probabilities = result[
            [f"{short_name}_p_{label}" for label in LABELS]
        ].to_numpy()
        result[f"{short_name}_brier"] = ((probabilities - target) ** 2).sum(axis=1)
    result["models_disagree"] = result["cardiff_label"].ne(
        result["distilbert_label"]
    )
    result["either_differs_from_majority"] = (
        result["cardiff_label"].ne(result["majority_label"])
        | result["distilbert_label"].ne(result["majority_label"])
    )
    result["mean_model_brier"] = result[
        ["cardiff_brier", "distilbert_brier"]
    ].mean(axis=1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--selected-out", type=Path)
    parser.add_argument("--selected-reference-out", type=Path)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    frame = read_dynasent(args.jsonl)
    for short_name in MODELS:
        frame = pd.concat(
            [frame, run_model(frame, short_name, args.batch_size)], axis=1
        )
    frame = add_audit_columns(frame)
    frame = frame.sort_values(
        ["models_disagree", "vote_pattern", "mean_model_brier"],
        ascending=[False, False, False],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False)

    selected = frame.set_index("item_id").loc[SELECTED_IDS].reset_index()
    if args.selected_out:
        release_columns = [
            "item_id",
            "sentence",
            "collection_round",
            "negative_votes",
            "neutral_votes",
            "positive_votes",
        ]
        args.selected_out.parent.mkdir(parents=True, exist_ok=True)
        selected[release_columns].to_csv(args.selected_out, index=False)
    if args.selected_reference_out:
        args.selected_reference_out.parent.mkdir(parents=True, exist_ok=True)
        selected.to_csv(args.selected_reference_out, index=False)

    print("candidate items:", len(frame))
    print("models disagree:", int(frame["models_disagree"].sum()))
    print(pd.crosstab(frame["cardiff_label"], frame["distilbert_label"]))
    print(
        "selected model disagreements:",
        int(selected["models_disagree"].sum()),
        "of",
        len(selected),
    )
    print("wrote:", args.out)


if __name__ == "__main__":
    main()
