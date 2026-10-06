#!/usr/bin/env python3
"""Assemble the four student project-data bundles from frozen course data.

The Wright export supplies the real data and cached model outputs.  The course
repository supplies the starter notebooks and documentation.  This script
combines them without changing the frozen source export.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil

import nbformat
import numpy as np


TRACKS = (
    "track_1_food",
    "track_2_pets",
    "track_3_preferences",
    "track_4_instructions",
)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def copy_templates(template_root: Path, output_root: Path) -> None:
    for track in TRACKS:
        for name in ("starter.ipynb", "datasheet.md", "system_card.md"):
            shutil.copy2(template_root / track / name, output_root / track / name)


def install_text_outputs(remote_root: Path, output_root: Path) -> None:
    text_root = remote_root / "text_full_v1"

    preferences = output_root / "track_3_preferences"
    pairs = read_jsonl(preferences / "data" / "pairs.jsonl")
    for record in pairs:
        record["response_A"] = record.pop("resp_A")
        record["response_B"] = record.pop("resp_B")
    write_jsonl(preferences / "data" / "pairs.jsonl", pairs)
    (preferences / "ai_outputs").mkdir(exist_ok=True)
    shutil.copy2(
        text_root / "shp" / "judge_outputs.jsonl",
        preferences / "ai_outputs" / "judge_outputs.jsonl",
    )

    instructions = output_root / "track_4_instructions"
    ifeval = text_root / "ifeval"
    (instructions / "ai_outputs").mkdir(exist_ok=True)
    shutil.copy2(ifeval / "metadata.csv", instructions / "metadata.csv")
    shutil.copy2(ifeval / "rule_checks.csv", instructions / "ai_outputs" / "rule_checks.csv")
    shutil.copy2(
        ifeval / "judge_outputs.jsonl",
        instructions / "ai_outputs" / "judge_outputs.jsonl",
    )

    prompts = {
        record["prompt_id"]: record["prompt"]
        for record in read_jsonl(ifeval / "selection.jsonl")
    }
    responses = read_jsonl(ifeval / "responses.jsonl")
    for record in responses:
        record["prompt"] = prompts[record["prompt_id"]]
        record["length_tokens"] = len(record["response"].split())
    write_jsonl(instructions / "data" / "responses.jsonl", responses)

    with (instructions / "metadata.csv").open(newline="", encoding="utf-8") as handle:
        metadata = list(csv.DictReader(handle))
    prompt_families = {
        (row["prompt_id"], row["constraint_family"]) for row in metadata
    }
    rng = np.random.default_rng(2027)
    holdout_prompts: set[str] = set()
    for family in sorted({family for _, family in prompt_families}):
        family_prompts = sorted(
            prompt_id for prompt_id, value in prompt_families if value == family
        )
        n_holdout = max(1, round(0.20 * len(family_prompts)))
        holdout_prompts.update(
            rng.choice(family_prompts, size=n_holdout, replace=False).tolist()
        )
    with (instructions / "splits.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "split"))
        writer.writeheader()
        for row in metadata:
            writer.writerow(
                {
                    "item_id": row["response_id"],
                    "split": (
                        "holdout"
                        if row["prompt_id"] in holdout_prompts
                        else "analysis"
                    ),
                }
            )


def release_datasheet(text: str, track: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not line.startswith("> ⚠️ **The data shipped in this folder")
    ]
    text = "\n".join(lines).replace(
        "15–25 categories (placeholder ships 18), 100–200 train + 50–100 test images per category",
        "18 categories × 80 images (1,440 total)",
    ).replace(
        "all 37 breeds at modest size (placeholder ships ~65 test images/breed, ~2,405 total), or a curated confusable-breed set",
        "all 37 breeds × 65 images (2,405 total)",
    ).replace(
        "4–6 domains × 500–1,000 examples (placeholder ships 5 domains × 180 = 900 pairs)",
        "5 domains × 180 examples (900 pairs total)",
    ).replace(
        "100–200 prompts × 2–3 precomputed responses (placeholder ships 150 prompts × 2 = 300 responses)",
        "150 prompts × 2 precomputed responses (300 responses total)",
    )
    for sentence in (
        " **The placeholder data here is CC0 synthetic — it contains no real images.**",
        " **The placeholder data here is CC0 synthetic — the texts are nonsense tokens, not real Reddit content.**",
        " **The placeholder data here is CC0 synthetic — the responses are filler tokens.**",
    ):
        text = text.replace(sentence, "")
    if track == "track_3_preferences":
        text = text.replace(
            "Cached LLM-judge decisions, one record per (pair, prompt_version):",
            "Cached Mistral-7B-Instruct-v0.3 judge decisions, one record per (pair, prompt_version):",
        )
    if track == "track_4_instructions":
        text = text.replace(
            "`judge_outputs.jsonl`: cached LLM-judge, one record per (response, prompt_version),",
            "`judge_outputs.jsonl`: cached Mistral-Nemo-Instruct-2407 judge output, one record per (response, prompt_version),",
        )
    return text.rstrip() + "\n"


def release_notebook(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    replacements = {
        "The checked-in data are development fixtures until staff installs the real teaching bundle; fixture results are not findings.":
            "This notebook uses the frozen Spring 2027 teaching bundle; keep the holdout sealed until the course release point.",
        "The checked-in texts and outputs are development fixtures until staff installs the real teaching bundle; fixture results are not findings. The holdout remains sealed.":
            "This notebook uses the frozen Spring 2027 teaching bundle. The holdout remains sealed until the course release point.",
        "The checked-in prompts, responses, and outputs are development fixtures until staff installs the real teaching bundle; fixture results are not findings. The holdout remains sealed.":
            "This notebook uses the frozen Spring 2027 teaching bundle. The holdout remains sealed until the course release point.",
    }
    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            for old, new in replacements.items():
                cell.source = cell.source.replace(old, new)
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    nbformat.write(notebook, path)


def write_readme(output_root: Path) -> None:
    (output_root / "README.md").write_text(
        """# Spring 2027 final-project data

Download only the track your team is using. Each bundle contains the frozen
course subset, cached AI outputs, analysis/holdout split, starter notebook,
datasheet, and system card.

Do not inspect holdout cases until the course-designated release point. The
cached outputs are part of the data-generating process: retain raw responses
and parse-error fields when analyzing them.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-root", type=Path, required=True)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    if args.output_root.exists():
        raise SystemExit(f"Output directory already exists: {args.output_root}")
    args.output_root.mkdir(parents=True)
    for track in TRACKS:
        shutil.copytree(args.remote_root / track, args.output_root / track)
    copy_templates(args.template_root, args.output_root)
    install_text_outputs(args.remote_root, args.output_root)

    for track in TRACKS:
        datasheet = args.output_root / track / "datasheet.md"
        datasheet.write_text(
            release_datasheet(datasheet.read_text(encoding="utf-8"), track),
            encoding="utf-8",
        )
        release_notebook(args.output_root / track / "starter.ipynb")
    write_readme(args.output_root)

    manifest = {
        "release": "spring-2027",
        "seed": 2027,
        "tracks": {},
    }
    for track in TRACKS:
        files = [path for path in (args.output_root / track).rglob("*") if path.is_file()]
        manifest["tracks"][track] = {
            "files": len(files),
            "bytes": sum(path.stat().st_size for path in files),
        }
    manifest_path = args.output_root / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
