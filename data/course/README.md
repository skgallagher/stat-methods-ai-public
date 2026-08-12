# Student release data

This directory contains frozen, licensed, privacy-reviewed teaching subsets.
The current student release includes:

- `camera_traps/`: 216 resized Caltech Camera Traps images in 72 complete
  trigger sequences from 12 camera locations;
- `dynasent/`: disjoint DynaSent v1.1 lab, homework, and forecaster subsets.

See each dataset directory's README for its source, license, construction, and
interpretation limits.

Do **not** copy `data/smoke/` here: those files are synthetic tests and are not
student data. Later release gates will add `cfpb`, `nhanes`, and
`designed_eval`.

After changing an approved release, rebuild the download manifest with:

```bash
python scripts/build_course_data_manifest.py --release-id spring27-week02-v1
```

The generated `manifest.json` records every distributed relative path, byte
count, and SHA-256 hash. Student notebooks use it to download only the groups
they need from the public GitHub repository, one file at a time, without a ZIP
archive or Drive mount.
