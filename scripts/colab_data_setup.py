"""Shared direct-from-GitHub setup cell for generated Colab notebooks."""

from __future__ import annotations


PUBLIC_REPO_RAW_URL = (
    "https://raw.githubusercontent.com/skgallagher/stat-methods-ai-public/main"
)


def build_setup(groups: list[str]) -> str:
    """Return a self-contained setup cell for the requested dataset groups."""
    group_literal = repr(groups)
    return f"""# Standard Colab setup - run once
from pathlib import Path
import hashlib
import json
import random
import sys
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 2027
random.seed(SEED)
np.random.seed(SEED)

COURSE_REPO_RAW_URL = {PUBLIC_REPO_RAW_URL!r}
COURSE_DATA_BASE_URL = COURSE_REPO_RAW_URL + '/data/course'
COURSE_DATA_GROUPS = {group_literal}
DATA_ROOT = Path('/content/stat_ai_data')

# Local repository runs use the frozen release when present and otherwise the
# synthetic smoke fixture. A fresh Colab downloads verified individual files
# from GitHub - no ZIP upload or Drive mount is required.
LOCAL_RELEASE = Path.cwd() / 'data' / 'course'
LOCAL_SMOKE = Path.cwd() / 'data' / 'smoke'
online_release = False
if (LOCAL_RELEASE / 'manifest.json').exists():
    DATA_ROOT = LOCAL_RELEASE
    data_source = 'local frozen release'
elif LOCAL_SMOKE.exists():
    DATA_ROOT = LOCAL_SMOKE
    data_source = 'local synthetic smoke fixture (development only)'
elif (DATA_ROOT / 'manifest.json').exists():
    cached_manifest = json.loads((DATA_ROOT / 'manifest.json').read_text())
    if 'smoke fixture' in cached_manifest.get('bundle_type', ''):
        data_source = 'existing local synthetic smoke fixture (development only)'
    else:
        cached_files = cached_manifest.get('files', [])
        requested_files = [
            item for item in cached_files
            if Path(item['path']).parts[0] in COURSE_DATA_GROUPS
        ]
        def cached_sha256(path):
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            return digest.hexdigest()
        cache_complete = (
            cached_manifest.get('release_status') == 'student_release'
            and requested_files
            and all(
                (DATA_ROOT / item['path']).exists()
                and cached_sha256(DATA_ROOT / item['path']) == item['sha256']
                for item in requested_files
            )
        )
        if cache_complete:
            data_source = 'existing verified runtime cache'
        else:
            online_release = True
else:
    online_release = True

if online_release:
    helper_target = Path('/content/course_helpers/__init__.py')
    helper_target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(
        COURSE_REPO_RAW_URL + '/course_helpers/__init__.py', helper_target
    )
    if '/content' not in sys.path:
        sys.path.insert(0, '/content')
    from course_helpers import ensure_course_data
    DATA_ROOT = ensure_course_data(
        COURSE_DATA_BASE_URL,
        DATA_ROOT,
        groups=COURSE_DATA_GROUPS,
    )
    data_source = 'public GitHub student release'

print('Setup complete. Data root:', DATA_ROOT)
print('Data source:', data_source)
print('Requested groups:', COURSE_DATA_GROUPS)
"""
