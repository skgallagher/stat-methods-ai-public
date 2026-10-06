"""Freeze the public Week 2 CFPB and DynaSent teaching extracts.

This script is instructor-side release infrastructure. It expects an official
DynaSent v1.1 directory and one or more CFPB API JSON responses. It creates
disjoint lab/homework DynaSent extracts, adds one pinned model's probability
reports, and writes a compact CFPB narrative extract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import pipeline


LABELS = ("negative", "neutral", "positive")
CARDIFF_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
CARDIFF_REVISION = "3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7"
SEED = 2027

# Each extract has 36 items from each round. These agreement-pattern quotas
# closely track the eligible five-judgment training pools while guaranteeing
# all three patterns appear in both rounds. They are part of the teaching-subset
# design and must be disclosed before students interpret round comparisons.
LAB_QUOTAS = {
    1: {"5-0": 11, "4-1": 15, "3-2": 10},
    2: {"5-0": 21, "4-1": 9, "3-2": 6},
}
HOMEWORK_QUOTAS = {
    1: {"5-0": 10, "4-1": 15, "3-2": 11},
    2: {"5-0": 20, "4-1": 10, "3-2": 6},
}


def read_dynasent(directory: Path) -> pd.DataFrame:
    rows: list[dict] = []
    files = {
        1: directory / "dynasent-v1.1-round01-yelp-train.jsonl",
        2: directory / "dynasent-v1.1-round02-dynabench-train.jsonl",
    }
    for round_number, path in files.items():
        with path.open() as stream:
            for line in stream:
                item = json.loads(line)
                distribution = item["label_distribution"]
                counts = {label: len(distribution.get(label, [])) for label in LABELS}
                if len(distribution.get("mixed", [])) or sum(counts.values()) != 5:
                    continue
                ordered = sorted(counts.values(), reverse=True)
                pattern = f"{ordered[0]}-{ordered[1]}"
                if pattern not in {"5-0", "4-1", "3-2"}:
                    continue
                sentence = re.sub(r"\s+", " ", item["sentence"]).strip()
                if not 20 <= len(sentence) <= 280:
                    continue
                rows.append(
                    {
                        "item_id": item["text_id"],
                        "sentence": sentence,
                        "collection_round": round_number,
                        **{f"{label}_votes": counts[label] for label in LABELS},
                        "vote_pattern": pattern,
                    }
                )
    return pd.DataFrame(rows).drop_duplicates("sentence").reset_index(drop=True)


def draw_extract(
    pool: pd.DataFrame,
    quotas: dict[int, dict[str, int]],
    used_ids: set[str],
    seed: int,
) -> pd.DataFrame:
    draws = []
    for round_number, pattern_quotas in quotas.items():
        for pattern, size in pattern_quotas.items():
            eligible = pool.loc[
                pool["collection_round"].eq(round_number)
                & pool["vote_pattern"].eq(pattern)
                & ~pool["item_id"].isin(used_ids)
            ]
            draws.append(eligible.sample(size, random_state=seed + 10 * round_number + size))
    result = pd.concat(draws).sample(frac=1, random_state=seed).reset_index(drop=True)
    used_ids.update(result["item_id"])
    return result


def add_model_probabilities(frame: pd.DataFrame, cache_dir: Path | None) -> pd.DataFrame:
    classifier = pipeline(
        "text-classification",
        model=CARDIFF_MODEL,
        revision=CARDIFF_REVISION,
        top_k=None,
        device=-1,
        model_kwargs={"cache_dir": str(cache_dir)} if cache_dir else {},
    )
    outputs = classifier(frame["sentence"].tolist(), truncation=True, batch_size=16)
    records = []
    for output in outputs:
        scores = {entry["label"].lower(): float(entry["score"]) for entry in output}
        records.append(
            {
                **{f"model_p_{label}": scores[label] for label in LABELS},
                "model_label": max(LABELS, key=scores.get),
            }
        )
    result = pd.concat([frame.reset_index(drop=True), pd.DataFrame(records)], axis=1)
    return result.drop(columns="vote_pattern")


def read_cfpb(paths: list[Path]) -> pd.DataFrame:
    records = []
    for path in paths:
        response = json.loads(path.read_text())
        records.extend(hit["_source"] for hit in response["hits"]["hits"])
    frame = pd.DataFrame(records).drop_duplicates("complaint_id")
    frame = frame.rename(columns={"complaint_what_happened": "narrative"})
    frame["narrative"] = frame["narrative"].fillna("").str.strip()
    frame = frame.loc[frame["narrative"].ne("")].copy()
    normalized = frame["narrative"].str.lower().str.replace(r"\s+", " ", regex=True)
    frame["similarity_group"] = normalized.map(
        lambda text: hashlib.sha256(text.encode()).hexdigest()[:12]
    )
    frame["duplicate_flag"] = frame.duplicated("similarity_group", keep=False)
    frame["n_words"] = frame["narrative"].str.split().str.len()
    columns = [
        "complaint_id",
        "narrative",
        "product",
        "issue",
        "date_received",
        "submitted_via",
        "similarity_group",
        "duplicate_flag",
        "n_words",
    ]
    frame = frame[columns].sort_values(["date_received", "complaint_id"])
    # Preserve all available submission modes in this small teaching extract.
    # The API calls are deliberately stratified, so a global head() would erase
    # the design feature the lab asks students to notice.
    return (
        frame.groupby("submitted_via", group_keys=False)
        .head(100)
        .sort_values(["date_received", "complaint_id"])
        .reset_index(drop=True)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dynasent-dir", type=Path, required=True)
    parser.add_argument("--cfpb-json", type=Path, nargs="+", required=True)
    parser.add_argument("--forecaster-items", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--hf-cache", type=Path)
    args = parser.parse_args()

    pool = read_dynasent(args.dynasent_dir)
    used_ids: set[str] = set(pd.read_csv(args.forecaster_items)["item_id"])
    lab = draw_extract(pool, LAB_QUOTAS, used_ids, SEED)
    homework = draw_extract(pool, HOMEWORK_QUOTAS, used_ids, SEED + 100)
    lab = add_model_probabilities(lab, args.hf_cache)
    homework = add_model_probabilities(homework, args.hf_cache)
    cfpb = read_cfpb(args.cfpb_json)

    dynasent_out = args.out / "dynasent"
    cfpb_out = args.out / "cfpb"
    dynasent_out.mkdir(parents=True, exist_ok=True)
    cfpb_out.mkdir(parents=True, exist_ok=True)
    lab.to_csv(dynasent_out / "items.csv", index=False)
    homework.to_csv(dynasent_out / "homework_items.csv", index=False)
    pd.read_csv(args.forecaster_items).to_csv(
        dynasent_out / "forecaster_items.csv", index=False
    )
    cfpb.to_csv(cfpb_out / "complaints.csv", index=False)

    assert set(lab["item_id"]).isdisjoint(homework["item_id"])
    assert len(lab) == len(homework) == 72
    assert len(cfpb) >= 100
    for frame in (lab, homework):
        assert frame[[f"{label}_votes" for label in LABELS]].sum(axis=1).eq(5).all()
        assert np.allclose(
            frame[[f"model_p_{label}" for label in LABELS]].sum(axis=1), 1
        )

    print("lab items:", len(lab))
    print(pd.crosstab(lab["collection_round"], lab[[f"{x}_votes" for x in LABELS]].max(axis=1)))
    print("homework items:", len(homework))
    print("CFPB narratives:", len(cfpb), "exact-duplicate rows:", int(cfpb["duplicate_flag"].sum()))


if __name__ == "__main__":
    main()
