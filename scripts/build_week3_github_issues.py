#!/usr/bin/env python3
"""Build the frozen Week 3 scikit-learn issue-triage teaching extract.

The extract intentionally contains only short issue titles and public metadata.
Issue bodies, comments, and GitHub usernames are not redistributed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


REPOSITORY = "scikit-learn/scikit-learn"
CREATED_RANGE = "2018-01-01..2025-12-31"
SNAPSHOT_DATE = "2026-08-12"
N_PER_MODULE = 15
MODULES = [
    "module:cluster",
    "module:ensemble",
    "module:linear_model",
    "module:metrics",
    "module:model_selection",
    "module:preprocessing",
    "module:tree",
    "module:utils",
]

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "course" / "github_issues"


def github_search(module: str) -> list[dict]:
    query = (
        f'repo:{REPOSITORY} is:issue is:closed label:"{module}" '
        f"created:{CREATED_RANGE}"
    )
    command = [
        "gh",
        "api",
        "-X",
        "GET",
        "search/issues",
        "-f",
        f"q={query}",
        "-f",
        "per_page=100",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)["items"]


def evenly_spaced(records: list[dict], n: int) -> list[dict]:
    if len(records) < n:
        raise ValueError(f"Need {n} eligible records, found {len(records)}")
    if n == 1:
        return [records[len(records) // 2]]
    indices = [round(j * (len(records) - 1) / (n - 1)) for j in range(n)]
    return [records[index] for index in indices]


def reporter_group(login: str) -> str:
    digest = hashlib.sha256(f"stat-ai-week3::{login}".encode()).hexdigest()[:10]
    return f"reporter_{digest}"


def main() -> None:
    selected: list[dict] = []
    eligibility_counts: dict[str, int] = {}

    for module in MODULES:
        eligible = []
        for item in github_search(module):
            module_labels = sorted(
                label["name"]
                for label in item.get("labels", [])
                if label["name"].startswith("module:")
            )
            if module_labels != [module]:
                continue
            if not item.get("title") or not item.get("user", {}).get("login"):
                continue
            eligible.append(item)

        eligible.sort(key=lambda item: (item["created_at"], item["number"]))
        eligibility_counts[module] = len(eligible)
        selected.extend(evenly_spaced(eligible, N_PER_MODULE))

    numbers = [item["number"] for item in selected]
    if len(numbers) != len(set(numbers)):
        raise ValueError("An issue was selected for more than one module")

    rows = []
    for item in selected:
        module = next(
            label["name"]
            for label in item["labels"]
            if label["name"].startswith("module:")
        )
        created_date = item["created_at"][:10]
        rows.append(
            {
                "issue_number": item["number"],
                "title": " ".join(item["title"].split()),
                "created_date": created_date,
                "created_year": created_date[:4],
                "module_label": module,
                "reporter_group": reporter_group(item["user"]["login"]),
                "source_url": item["html_url"],
            }
        )

    rows.sort(key=lambda row: (row["created_date"], row["issue_number"]))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "issues.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "source_repository": REPOSITORY,
        "snapshot_date": SNAPSHOT_DATE,
        "created_range": CREATED_RANGE,
        "selection": f"{N_PER_MODULE} issues with exactly one module label",
        "modules": MODULES,
        "rows": len(rows),
        "eligible_records_by_module_before_sampling": eligibility_counts,
    }
    (OUTPUT_DIR / "release_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {csv_path} with {len(rows)} real issue records")
    print(json.dumps(eligibility_counts, indent=2))


if __name__ == "__main__":
    main()
