"""Build the per-file manifest used by the public GitHub data downloader."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = ROOT / "data" / "course"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(data_root: Path, release_id: str) -> dict:
    if not data_root.exists():
        raise FileNotFoundError(f"Course-data directory does not exist: {data_root}")
    files = []
    for path in sorted(data_root.rglob("*")):
        if not path.is_file() or path.name in {"manifest.json", "README.md"}:
            continue
        relative = path.relative_to(data_root).as_posix()
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    if not files:
        raise ValueError("Refusing to create an empty student-release manifest.")
    return {
        "schema_version": 1,
        "release_status": "student_release",
        "release_id": release_id,
        "delivery": "individual files from the public GitHub repository; no ZIP archive",
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--release-id", required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.data_root.resolve(), args.release_id)
    output = args.data_root.resolve() / "manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {output} with {len(manifest['files'])} files")


if __name__ == "__main__":
    main()
