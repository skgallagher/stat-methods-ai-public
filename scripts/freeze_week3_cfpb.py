"""Freeze the time- and product-stratified CFPB extract used from Week 3 onward.

The official API is queried twice for each product-year cell: once from the
start of the year and once from the end. A deterministic hash draw selects 20
public narratives per cell. When a candidate cell contains an exact normalized
duplicate pair, one pair is retained deliberately so grouped-split exercises
have real repeated templates to inspect.

The written CSV is the frozen release. A later rerun can differ because the
public database may revise historical records; the release summary records the
API timestamp and construction choices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import urllib.parse
from pathlib import Path

import pandas as pd


API_URL = (
    "https://www.consumerfinance.gov/data-research/consumer-complaints/"
    "search/api/v1/"
)
YEARS = (2022, 2023, 2024, 2025)
PRODUCTS = (
    "Checking or savings account",
    "Debt collection",
    "Mortgage",
    "Student loan",
    "Vehicle loan or lease",
)
PER_CELL = 20
SEED = 2027


def normalize_narrative(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def stable_hash(value: str) -> str:
    return hashlib.sha256(f"{SEED}|{value}".encode()).hexdigest()


def fetch_cell(year: int, product: str, sort: str) -> tuple[pd.DataFrame, dict]:
    params = {
        "date_received_min": f"{year}-01-01",
        # The production API currently treats this boundary as inclusive even
        # though the OpenAPI description says "date < max".
        "date_received_max": f"{year}-12-31",
        "field": "all",
        "has_narrative": "true",
        "no_aggs": "true",
        "product": product,
        "size": 100,
        "sort": sort,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    completed = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", url],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    rows = [hit["_source"] for hit in payload["hits"]["hits"]]
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError(f"No CFPB rows returned for {year}, {product}, {sort}")
    return frame, payload.get("_meta", {})


def select_cell(candidates: pd.DataFrame, year: int, product: str) -> pd.DataFrame:
    candidates = candidates.drop_duplicates("complaint_id").copy()
    candidates["narrative"] = candidates["complaint_what_happened"].fillna("").str.strip()
    candidates = candidates.loc[candidates["narrative"].ne("")].copy()
    candidates["normalized_narrative"] = candidates["narrative"].map(normalize_narrative)
    candidates["selection_rank"] = candidates["complaint_id"].astype(str).map(stable_hash)

    # Preserve at most one real repeated-template pair per product-year cell.
    repeated = candidates.loc[
        candidates.duplicated("normalized_narrative", keep=False)
    ].copy()
    pair = candidates.iloc[0:0].copy()
    if not repeated.empty:
        repeated["group_rank"] = repeated["normalized_narrative"].map(stable_hash)
        chosen_group = repeated.sort_values(
            ["group_rank", "selection_rank"]
        )["normalized_narrative"].iloc[0]
        pair = repeated.loc[repeated["normalized_narrative"].eq(chosen_group)].sort_values(
            "selection_rank"
        ).head(2)

    remaining = candidates.loc[~candidates["complaint_id"].isin(pair["complaint_id"])].sort_values(
        "selection_rank"
    )
    selected = pd.concat([pair, remaining.head(PER_CELL - len(pair))], ignore_index=True)
    if len(selected) != PER_CELL:
        raise RuntimeError(
            f"Needed {PER_CELL} narratives for {year}, {product}; found {len(selected)}"
        )
    selected["received_year"] = year
    selected["period"] = "source" if year <= 2023 else "target"
    selected["sample_cell"] = f"{year} | {product}"
    return selected


def build_release() -> tuple[pd.DataFrame, dict]:
    selected_cells = []
    api_meta = []
    for year in YEARS:
        for product in PRODUCTS:
            frames = []
            for sort in ("created_date_asc", "created_date_desc"):
                frame, meta = fetch_cell(year, product, sort)
                frames.append(frame)
                api_meta.append(meta)
            candidates = pd.concat(frames, ignore_index=True)
            selected_cells.append(select_cell(candidates, year, product))

    release = pd.concat(selected_cells, ignore_index=True)
    release["similarity_group"] = release["normalized_narrative"].map(
        lambda value: hashlib.sha256(value.encode()).hexdigest()[:12]
    )
    release["duplicate_flag"] = release.duplicated("similarity_group", keep=False)
    release["n_words"] = release["narrative"].str.split().str.len()
    release["source_url"] = release["complaint_id"].map(
        lambda value: f"{API_URL}{value}"
    )
    release = release.rename(columns={"date_received": "date_received"})
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
        "received_year",
        "period",
        "sample_cell",
        "source_url",
    ]
    release = release[columns].sort_values(
        ["date_received", "product", "complaint_id"]
    ).reset_index(drop=True)

    counts = release.groupby(["received_year", "product"]).size()
    assert len(release) == len(YEARS) * len(PRODUCTS) * PER_CELL
    assert counts.eq(PER_CELL).all()
    if not release["complaint_id"].is_unique:
        duplicates = release.loc[
            release.duplicated("complaint_id", keep=False),
            ["complaint_id", "received_year", "product", "date_received"],
        ]
        raise RuntimeError(
            "Complaint IDs crossed sampling cells:\n" + duplicates.to_string(index=False)
        )
    assert release["narrative"].ne("").all()
    assert set(release["received_year"]) == set(YEARS)

    last_updated = sorted(
        {meta.get("last_updated") for meta in api_meta if meta.get("last_updated")}
    )
    summary = {
        "release_id": "cfpb-week3-v2-2026-09-01",
        "source": "CFPB Consumer Complaint Database API",
        "license": "CC0",
        "rows": int(len(release)),
        "years": list(YEARS),
        "products": list(PRODUCTS),
        "rows_per_product_year": PER_CELL,
        "duplicate_rows": int(release["duplicate_flag"].sum()),
        "similarity_groups": int(release["similarity_group"].nunique()),
        "api_last_updated": last_updated,
        "sampling_note": (
            "Product-by-year stratified teaching extract; not a probability sample and "
            "not representative of natural product prevalence. Candidate pools combine "
            "the first and last 100 public narratives in each product-year cell."
        ),
    }
    return release, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/course/cfpb"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    release, summary = build_release()
    release.to_csv(args.output_dir / "complaints.csv", index=False)
    (args.output_dir / "release_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
