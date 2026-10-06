# Student release data

This directory contains frozen, licensed, privacy-reviewed teaching subsets.

- `camera_traps/`: 216 resized Caltech Camera Traps images in 72 complete
  trigger sequences from 12 camera locations.
- `dynasent/`: the frozen Week 2 repeated-rater teaching subset.
- `cfpb/`: the current Week 3 structural prototype, pending replacement by a
  time-spanning complaint extract.
- `github_issues/`: 120 real scikit-learn issue titles and metadata for the
  Week 3 issue-triage design problem.

See each group README for source, license, selection, privacy, and statistical
limitations.

Do **not** copy `data/smoke/` here: those files are synthetic tests and are not
student data. Later releases will add `nhanes` and `designed_eval` after their
separate release gates pass.

After changing an approved release, rebuild the download manifest with:

```bash
python scripts/build_course_data_manifest.py --release-id spring27-v1
```

The generated `manifest.json` records every distributed relative path, byte
count, and SHA-256 hash. Student notebooks use it to download only the groups
they need from the public GitHub repository, one file at a time, without a ZIP
archive or Drive mount.
