# Student release data

This directory contains frozen, licensed, privacy-reviewed teaching subsets.
The Spring 2027 Week 1 release currently includes `camera_traps/`: 216 resized
Caltech Camera Traps images in 72 complete trigger sequences from 12 camera
locations. See `camera_traps/README.md` and `release_summary.json` for source,
license, selection, model-output, and split details.

Do **not** copy `data/smoke/` here: those files are synthetic tests and are not
student data. Later releases will add `cfpb`, `dynasent`, `nhanes`, and
`designed_eval` after their separate release gates pass.

After changing an approved release, rebuild the download manifest with:

```bash
python scripts/build_course_data_manifest.py --release-id spring27-v1
```

The generated `manifest.json` records every distributed relative path, byte
count, and SHA-256 hash. Student notebooks use it to download only the groups
they need from the public GitHub repository, one file at a time, without a ZIP
archive or Drive mount.
