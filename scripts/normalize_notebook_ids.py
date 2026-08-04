"""Add deterministic cell IDs to hand-authored notebooks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def normalize(path: Path) -> None:
    notebook = json.loads(path.read_text())
    stem = path.stem.replace("_", "-")[:24]
    for index, cell in enumerate(notebook["cells"]):
        cell["id"] = f"{stem}-{index:03d}"
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    print(f"normalized {path}")


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        normalize(Path(argument))
