"""Execute the generated Week 2 lab and homework starters on smoke data."""

from __future__ import annotations

import shutil
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
PILOT = Path("/private/tmp/stat_ai_week2_pilot")
DATA = ROOT / "data" / "smoke"


def execute(source: Path, destination: Path) -> dict:
    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            if source.name == "lab.ipynb":
                cell.source = cell.source.replace(
                    "items = pd.read_csv(DATA_URL)",
                    f"items = pd.read_csv({str(ROOT / 'data' / 'course' / 'dynasent' / 'items.csv')!r})",
                )
            cell.source = cell.source.replace(
                "DATA_ROOT = Path('/content/stat_ai_data')",
                f"DATA_ROOT = Path({str(DATA)!r})",
            )
            if "# Standard Colab setup" in cell.source:
                cell.source += (
                    "\nimport sys\n"
                    f"sys.path.insert(0, {str(ROOT)!r})\n"
                )
            if source.name == "hw02_starter.ipynb":
                cell.source = cell.source.replace(
                    "student_forecasts['student_p_negative'] = [np.nan] * len(student_forecasts)",
                    "student_forecasts['student_p_negative'] = [0.34] * len(student_forecasts)",
                ).replace(
                    "student_forecasts['student_p_neutral'] = [np.nan] * len(student_forecasts)",
                    "student_forecasts['student_p_neutral'] = [0.33] * len(student_forecasts)",
                ).replace(
                    "student_forecasts['student_p_positive'] = [np.nan] * len(student_forecasts)",
                    "student_forecasts['student_p_positive'] = [0.33] * len(student_forecasts)",
                )
    notebook.metadata.kernelspec = {
        "display_name": "Python (stat-ai)",
        "language": "python",
        "name": "stat-ai",
    }
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="stat-ai",
        resources={"metadata": {"path": str(ROOT)}},
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
    results = [
        execute(
            ROOT / "weeks" / "week02" / "lab.ipynb",
            PILOT / "lab02_executed.ipynb",
        ),
        execute(
            ROOT / "weeks" / "week02" / "hw02_starter.ipynb",
            PILOT / "hw02_executed.ipynb",
        ),
    ]
    for result in results:
        print(result)
    print(f"executed pilot artifacts: {PILOT}")


if __name__ == "__main__":
    main()
