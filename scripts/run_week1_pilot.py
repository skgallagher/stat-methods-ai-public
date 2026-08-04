"""Execute completed HW0, Lab 1, and the HW1 starter in a clean temp directory."""

from __future__ import annotations

import shutil
from pathlib import Path

import nbformat
from nbclient import NotebookClient
import pandas as pd
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
PILOT = Path("/private/tmp/stat_ai_week1_pilot")
COURSE_RELEASE = ROOT / "data" / "course"
DATA = COURSE_RELEASE if (COURSE_RELEASE / "manifest.json").exists() else ROOT / "data" / "smoke"


def validate_week1_data() -> dict:
    root = DATA / "camera_traps"
    data = (
        pd.read_csv(root / "metadata.csv")
        .merge(pd.read_csv(root / "image_features.csv"), on="image_id")
        .merge(pd.read_csv(root / "model_outputs.csv"), on="image_id")
        .merge(pd.read_csv(root / "splits.csv"), on="image_id")
    )
    features = ["brightness", "edge_density", "green_fraction", "night_indicator"]
    analysis = data.query("split == 'analysis'")
    model = LogisticRegression(max_iter=2000).fit(
        analysis[features], analysis["animal_present"]
    )
    result = {}
    for split in ["holdout_camera", "homework_holdout"]:
        evaluation = data.query("split == @split").copy()
        evaluation["baseline_pred"] = model.predict(evaluation[features])
        baseline_errors = int(
            evaluation["baseline_pred"].ne(evaluation["animal_present"]).sum()
        )
        vision_errors = int(
            evaluation["vision_pred"].ne(evaluation["animal_present"]).sum()
        )
        assert baseline_errors >= 2, f"{split}: baseline gallery cannot be built"
        assert vision_errors >= 2, f"{split}: vision gallery cannot be built"
        result[split] = {
            "rows": len(evaluation),
            "baseline_errors": baseline_errors,
            "vision_errors": vision_errors,
        }
    return result


def prepared_notebook(source: Path, *, complete_hw0: bool = False):
    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        cell.source = cell.source.replace(
            "DATA_ROOT = Path('/content/stat_ai_data')",
            f"DATA_ROOT = Path({str(DATA)!r})",
        )
        if complete_hw0:
            cell.source = cell.source.replace("sample_mean = ...  # TODO", "sample_mean = values.mean()")
    notebook.metadata.kernelspec = {
        "display_name": "Python (stat-ai)",
        "language": "python",
        "name": "stat-ai",
    }
    return notebook


def execute(source: Path, destination: Path, *, complete_hw0: bool = False) -> dict:
    notebook = prepared_notebook(source, complete_hw0=complete_hw0)
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="stat-ai",
        resources={"metadata": {"path": str(PILOT)}},
    )
    client.execute()
    nbformat.write(notebook, destination)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    return {
        "notebook": source.name,
        "code_cells": len(code_cells),
        "cells_with_output": sum(bool(cell.get("outputs")) for cell in code_cells),
    }


def main() -> None:
    if PILOT.exists():
        shutil.rmtree(PILOT)
    PILOT.mkdir(parents=True)
    if DATA == COURSE_RELEASE:
        shutil.copytree(COURSE_RELEASE, PILOT / "data" / "course")
    data_check = validate_week1_data()
    results = []
    hw0 = ROOT / "weeks" / "week00" / "hw00_colab_gradescope_check.ipynb"
    if hw0.exists():
        results.append(
            execute(hw0, PILOT / "hw00_executed.ipynb", complete_hw0=True)
        )
    results.extend(
        [
            execute(
                ROOT / "weeks" / "week01" / "lab_starter.ipynb",
                PILOT / "lab01_executed.ipynb",
            ),
            execute(
                ROOT / "weeks" / "week01" / "hw01_starter.ipynb",
                PILOT / "hw01_executed.ipynb",
            ),
        ]
    )
    for result in results:
        print(result)
    print({"week1_data": data_check, "data_source": str(DATA)})
    print(f"executed pilot artifacts: {PILOT}")


if __name__ == "__main__":
    main()
