"""Convert active lab QMD sources into student-facing Colab notebooks.

The converter preserves the QMD as the source of truth, creates one notebook cell
per instructional phase, converts relative data paths to DATA_ROOT, and inserts
the response/check cells that make the lab usable in class.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from colab_data_setup import build_setup


ROOT = Path(__file__).resolve().parents[1]
WEEKS = ["01", "02", "03", "04", "05", "06", "09", "10", "11", "12"]

DATA_GROUPS = {
    "01": ["camera_traps"],
    "02": ["cfpb", "dynasent"],
    "03": ["cfpb"],
    "04": ["camera_traps", "nhanes"],
    "05": ["cfpb"],
    "06": ["cfpb"],
    "09": ["cfpb"],
    "10": ["cfpb"],
    "11": ["designed_eval"],
    "12": ["designed_eval"],
}

WORKFLOW = """## How this Colab lab works

Use one shared team copy. One person is the **driver** and runs code; the other is the **statistical navigator** and checks the unit, denominator, split, and claim. Switch roles at the marked handoff.

1. Record the individual prediction before revealing output.
2. Run the instructor example.
3. Modify the supplied code with your partner.
4. Run the supplied structural check.
5. Inspect actual images or text when requested.
6. Write the independent handoff in your own words.

The notebook file is shared; each collaborator's temporary Colab runtime is not. Avoid two people executing different versions simultaneously. Save the notebook before switching drivers.
"""

PREDICTION = """### Individual response — before running output

TODO: record your prediction, estimand/unit, or design choice in 1–3 sentences.
"""

PAIR_RESPONSE = """### Pair record

**Driver:** TODO  
**Statistical navigator:** TODO  
**Result/check:** TODO  
**What the result supports—and does not:** TODO
"""

HANDOFF = """### Independent handoff

Write this individually before discussing wording with your partner.

TODO
"""

DISCUSSION_RESPONSE = """### Individual discussion response

Write your own answer before comparing wording with your partner.

TODO
"""

EXIT_RESPONSE = """### Exit-ticket response

TODO
"""

FINAL = """## Before leaving

- [ ] The notebook runs in order through the required handoff.
- [ ] Denominators, units, and evaluated population are visible.
- [ ] Required image/text cases are displayed rather than merely described.
- [ ] The driver and navigator switched at least once.
- [ ] Each person wrote the independent handoff.
- [ ] The named artifact was saved for the homework or project.
"""


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(True),
    }


def front_matter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        return "Lab", text
    title_match = re.search(r'^title:\s*"?(.*?)"?$', match.group(1), flags=re.M)
    title = title_match.group(1) if title_match else "Lab"
    return title, text[match.end():]


def split_markdown_sections(source: str) -> list[str]:
    pieces = re.split(r"(?=^## )", source, flags=re.M)
    return [piece.strip() for piece in pieces if piece.strip()]


def parse_qmd(body: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    position = 0
    pattern = re.compile(r"```\{python\}\n(.*?)\n```", flags=re.S)
    for match in pattern.finditer(body):
        markdown = body[position:match.start()]
        blocks.extend(("markdown", part) for part in split_markdown_sections(markdown))
        source = re.sub(r"^#\|\s*eval:\s*false\s*\n", "", match.group(1))
        source = re.sub(
            r"(['\"])\.\./\.\./data/([^'\"]+)\1",
            lambda m: f'DATA_ROOT / "{m.group(2)}"',
            source,
        )
        blocks.append(("code", source.strip()))
        position = match.end()
    blocks.extend(("markdown", part) for part in split_markdown_sections(body[position:]))
    return blocks


def build_lab(qmd: Path, week: str) -> dict:
    title, body = front_matter(qmd.read_text())
    cells = [md(f"# {title}\n"), md(WORKFLOW), code(build_setup(DATA_GROUPS[week]))]
    current_heading = ""
    response_added: set[str] = set()

    for kind, source in parse_qmd(body):
        if kind == "markdown":
            heading = re.search(r"^## ([^\n]+)", source)
            current_heading = heading.group(1).lower() if heading else current_heading
            cells.append(md(source))
            if "lecture bridge" in current_heading or "instructor run" in current_heading:
                key = f"predict:{current_heading}"
                if key not in response_added:
                    cells.append(md(PREDICTION))
                    response_added.add(key)
            elif "stop and discuss" in current_heading:
                cells.append(md(DISCUSSION_RESPONSE))
            elif "exit ticket" in current_heading:
                cells.append(md(EXIT_RESPONSE))
        else:
            cells.append(code(source))
            if any(word in current_heading for word in ["pairs", "modify", "analyze", "execute", "audit"]):
                key = f"pair:{current_heading}"
                if key not in response_added:
                    cells.append(md(PAIR_RESPONSE))
                    response_added.add(key)
            elif "handoff" in current_heading:
                cells.append(md(HANDOFF))

    if not any("### Independent handoff" in "".join(cell["source"]) for cell in cells):
        cells.append(md(HANDOFF))
    cells.append(md(FINAL))
    for index, cell in enumerate(cells):
        cell["id"] = f"lab{week}-{index:03d}"
    return {
        "cells": cells,
        "metadata": {
            "colab": {"name": f"week{week}_lab.ipynb", "provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    for week in WEEKS:
        qmd = ROOT / "weeks" / f"week{week}" / "lab.qmd"
        output = qmd.with_name("lab_starter.ipynb")
        notebook = build_lab(qmd, week)
        output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {output.relative_to(ROOT)} ({len(notebook['cells'])} cells)")


if __name__ == "__main__":
    main()
