"""Download and check the course data for a Stat-AI notebook.

Students only call setup_course(). Everything else in this file is plumbing:
it finds or downloads the requested data and checks every file against the
course manifest so a broken download is caught right away.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

RAW_URL = "https://raw.githubusercontent.com/skgallagher/stat-methods-ai-public/main"
DATA_URL = RAW_URL + "/data/course"


def _find_local_release() -> Path | None:
    """Return a local copy of the course data if this runs inside the course repository."""
    for folder in [Path.cwd(), *Path.cwd().parents]:
        candidate = folder / "data" / "course"
        if (candidate / "manifest.json").exists():
            return candidate
    return None


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _make_helpers_importable(repo_root: Path | None) -> None:
    """Let notebooks run `from course_helpers import ...`."""
    if repo_root is not None:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        return
    package = Path("course_helpers")
    package.mkdir(exist_ok=True)
    urllib.request.urlretrieve(f"{RAW_URL}/course_helpers/__init__.py", package / "__init__.py")
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))


def setup_course(*groups: str, destination: str | Path | None = None) -> Path:
    """Make the requested data groups available and return the data folder.

    Example: data_dir = setup_course("camera_traps")
    """
    local = _find_local_release()
    if local is not None:
        _make_helpers_importable(local.parents[1])
        print(f"Using the local course data in {local}")
        return local

    if destination is None:
        destination = Path("/content/stat_ai_data") if Path("/content").exists() else Path("stat_ai_data")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(f"{DATA_URL}/manifest.json") as response:
        manifest_bytes = response.read()
    manifest = json.loads(manifest_bytes)
    if manifest.get("release_status") != "student_release":
        raise ValueError("The course data online are not marked as a student release.")

    files = [item for item in manifest["files"] if Path(item["path"]).parts[0] in groups]
    found_groups = {Path(item["path"]).parts[0] for item in files}
    missing = sorted(set(groups) - found_groups)
    if missing:
        raise ValueError(f"These data groups are not in the course release: {missing}")

    downloaded = 0
    for item in files:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe path in the course manifest: {relative}")
        target = destination / relative
        if target.exists() and _sha256(target) == item["sha256"]:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(target.suffix + ".part")
        urllib.request.urlretrieve(f"{DATA_URL}/{relative.as_posix()}", partial)
        if _sha256(partial) != item["sha256"]:
            partial.unlink(missing_ok=True)
            raise ValueError(f"{relative} did not download correctly. Run this cell again.")
        partial.replace(target)
        downloaded += 1

    (destination / "manifest.json").write_bytes(manifest_bytes)
    _make_helpers_importable(None)
    print(f"Data ready: {', '.join(groups)} ({len(files)} files checked, {downloaded} downloaded)")
    return destination
