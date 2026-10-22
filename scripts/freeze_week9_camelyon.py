"""Freeze the Week 9 lab data: tissue patches from five hospitals and a model's predictions.

Camelyon17-WILDS (Koh et al. 2021, from the CAMELYON17 challenge; Bandi et al. 2019) has
96x96 patches of lymph-node slides from five Dutch hospitals, each labeled tumor or not.
WILDS lists it as public domain under CC0. This script reads a pinned revision of the
Hugging Face mirror `wltjr1007/Camelyon17-WILDS`, fetching only the parquet row groups it
needs (about 130 MB, not the full 10 GB).

The "AI system" is built here, on CPU: ImageNet ResNet-18 features (torchvision weights
IMAGENET1K_V1) followed by logistic regression, fitted on some slides from hospitals 1-3.
Other slides from hospitals 1-3 are the benchmark. Hospitals 4 and 5 are new hospitals
the model never saw. Only the benchmark and new-hospital patches are released, with the
model's predicted probability of tumor; the fitting patches and the model are not.

Usage:
    python scripts/freeze_week9_camelyon.py --work-dir WORK   # WORK caches the download
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "course" / "camelyon17"
REPO = "wltjr1007/Camelyon17-WILDS"
REVISION = "d784d5344ba6c967f83f9f3d9b2f1e2a4d6eb78f"
SEED = 2027
SHARDS = [f"validation-0000{i}-of-00003" for i in range(3)] + [f"test-0000{i}-of-00004" for i in range(4)]
# WILDS center codes -> the hospital numbers used in class (1-3 train, 4 validation, 5 test)
HOSPITAL = {0: 1, 3: 2, 4: 3, 1: 4, 2: 5}
PULL_PER_LABEL = {0: 800, 3: 800, 4: 800, 1: 300, 2: 300}   # by WILDS center
RELEASE_BENCHMARK_PER_HOSPITAL = 300
RELEASE_NEW_PER_LABEL = 150


def shard_path(shard: str) -> str:
    return f"datasets/{REPO}@{REVISION}/data/{shard}.parquet"


def row_group_stats(fs) -> pd.DataFrame:
    import pyarrow.parquet as pq
    rows = []
    for shard in SHARDS:
        with fs.open(shard_path(shard)) as fh:
            md = pq.ParquetFile(fh).metadata
        names = [md.schema.column(i).name for i in range(md.num_columns)]
        for g in range(md.num_row_groups):
            rg = md.row_group(g)
            rec = {"shard": shard, "group": g}
            for col in ["center", "label"]:
                st = rg.column(names.index(col)).statistics
                rec[col + "_min"], rec[col + "_max"] = st.min, st.max
            rows.append(rec)
    return pd.DataFrame(rows)


def pull(work: Path) -> tuple[np.ndarray, pd.DataFrame]:
    """Read label-balanced patches for every hospital, caching them in the work folder."""
    images_path, meta_path = work / "pulled_images.npy", work / "pulled_meta.csv"
    if images_path.exists() and meta_path.exists():
        return np.load(images_path), pd.read_csv(meta_path)
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    from PIL import Image

    fs = HfFileSystem()
    stats = row_group_stats(fs)
    chosen = set()
    for center, per_label in PULL_PER_LABEL.items():
        for label in [0, 1]:
            cand = stats[(stats.center_min <= center) & (stats.center_max >= center)
                         & (stats.label_min <= label) & (stats.label_max >= label)].reset_index(drop=True)
            pure = ((cand.center_min == cand.center_max) & (cand.label_min == cand.label_max)).all()
            need = int(np.ceil(per_label * (1.0 if pure else 3.0) / 100))
            for i in np.unique(np.linspace(0, len(cand) - 1, min(need, len(cand))).round().astype(int)):
                chosen.add((cand.loc[i, "shard"], int(cand.loc[i, "group"])))
    images, rows = [], []
    for shard in sorted({s for s, _ in chosen}):
        groups = sorted(g for s, g in chosen if s == shard)
        with fs.open(shard_path(shard)) as fh:
            df = pq.ParquetFile(fh).read_row_groups(groups).to_pandas()
        for _, r in df.iterrows():
            if r["center"] not in PULL_PER_LABEL:
                continue
            images.append(np.asarray(Image.open(io.BytesIO(r["image"]["bytes"])).convert("RGB"), dtype=np.uint8))
            rows.append({k: int(r[k]) for k in ["label", "center", "image_id", "patient", "node", "slide"]})
        print(f"{shard}: {len(groups)} row groups", flush=True)
    meta = pd.DataFrame(rows)
    images = np.stack(images)
    rng = np.random.default_rng(SEED)
    keep = []
    for (center, label), idx in sorted(meta.groupby(["center", "label"]).groups.items()):
        idx = np.array(sorted(idx))
        keep.extend(rng.choice(idx, min(len(idx), PULL_PER_LABEL[center]), replace=False))
    keep = np.sort(np.array(keep))
    images, meta = images[keep], meta.loc[keep].reset_index(drop=True)
    np.save(images_path, images)
    meta.to_csv(meta_path, index=False)
    return images, meta


def features(images: np.ndarray) -> np.ndarray:
    import torch
    import torchvision
    torch.manual_seed(SEED)
    net = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
    net.fc = torch.nn.Identity()
    net.eval()
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    out = []
    with torch.no_grad():
        for i in range(0, len(images), 256):
            x = torch.from_numpy(images[i:i + 256]).permute(0, 3, 1, 2).float() / 255
            out.append(net((x - mean) / std).numpy())
    return np.concatenate(out)


def main() -> None:
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)

    images, meta = pull(args.work_dir)
    meta["hospital"] = meta["center"].map(HOSPITAL)

    # Split hospitals 1-3 by slide: about a third of slides (with and without tumor) are the benchmark.
    rng = np.random.default_rng(SEED)
    meta["role"] = "new hospital"
    for h in [1, 2, 3]:
        has_tumor = meta[meta.hospital == h].groupby("slide")["label"].max()
        held = []
        for t in [0, 1]:
            slides = np.array(sorted(has_tumor[has_tumor == t].index))
            rng.shuffle(slides)
            held += list(slides[: max(1, int(round(len(slides) / 3)))])
        rows = meta.hospital == h
        meta.loc[rows, "role"] = np.where(meta.loc[rows, "slide"].isin(held), "benchmark", "fit")

    feats = features(images)
    fit = (meta.role == "fit").to_numpy()
    model = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=3000))
    model.fit(feats[fit], meta.loc[fit, "label"])
    meta["p_tumor"] = model.predict_proba(feats)[:, 1].round(4)
    fit_accuracy = float(((meta.loc[fit, "p_tumor"] >= 0.5).astype(int) == meta.loc[fit, "label"]).mean())

    # Choose the released patches.
    rng = np.random.default_rng(SEED + 1)
    release = []
    for h in [1, 2, 3]:
        idx = np.array(sorted(meta.index[(meta.hospital == h) & (meta.role == "benchmark")]))
        release.extend(rng.choice(idx, min(len(idx), RELEASE_BENCHMARK_PER_HOSPITAL), replace=False))
    for h in [4, 5]:
        for label in [0, 1]:
            idx = np.array(sorted(meta.index[(meta.hospital == h) & (meta.label == label)]))
            release.extend(rng.choice(idx, RELEASE_NEW_PER_LABEL, replace=False))
    release = np.sort(np.array(release))
    out_meta = meta.loc[release].reset_index(drop=True)
    out_images = images[release]
    out_meta.insert(0, "patch_id", [f"c17_{i:04d}" for i in range(1, len(out_meta) + 1)])
    out_meta["slide_id"] = "h" + out_meta.hospital.astype(str) + "_slide" + out_meta.slide.astype(str).str.zfill(2)
    out_meta["predicted_tumor"] = (out_meta.p_tumor >= 0.5).astype(int)
    out_meta["group"] = np.where(out_meta.role == "benchmark", "benchmark", "hospital " + out_meta.hospital.astype(str))
    columns = ["patch_id", "group", "hospital", "slide_id", "label", "p_tumor", "predicted_tumor"]
    out_meta = out_meta[columns]

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "patches.npz", images=out_images)
    out_meta.to_csv(OUT / "patches.csv", index=False)

    correct = out_meta.predicted_tumor == out_meta.label
    summary = {
        "source": f"Camelyon17-WILDS via the Hugging Face mirror {REPO}",
        "source_revision": REVISION,
        "license": "CC0 (public domain), as listed by WILDS",
        "model": "ImageNet ResNet-18 features (torchvision IMAGENET1K_V1) + logistic regression (C=0.1), fitted on other slides from hospitals 1-3",
        "seed": SEED,
        "fit_patches_not_released": int(fit.sum()),
        "fit_accuracy": round(fit_accuracy, 4),
        "released_patches": int(len(out_meta)),
        "by_group": {
            g: {"patches": int((out_meta.group == g).sum()),
                "slides": int(out_meta.loc[out_meta.group == g, "slide_id"].nunique()),
                "tumor_share": round(float(out_meta.loc[out_meta.group == g, "label"].mean()), 4),
                "accuracy": round(float(correct[out_meta.group == g].mean()), 4)}
            for g in ["benchmark", "hospital 4", "hospital 5"]
        },
        "patches_npz_sha256": hashlib.sha256((OUT / "patches.npz").read_bytes()).hexdigest(),
    }
    (OUT / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "README.md").write_text(README)
    print(json.dumps(summary, indent=2))


README = """# Week 9 lab data: Camelyon17 tissue patches

Small patches of lymph-node tissue slides from five hospitals in the Netherlands, each
labeled by pathologists as containing tumor or not, with a model's predicted probability
of tumor. Built by `scripts/freeze_week9_camelyon.py`.

## Files

- `patches.npz`: one array, `images`, of shape (patches, 96, 96, 3), uint8 RGB. Row *i*
  is the patch in row *i* of `patches.csv`.
- `patches.csv`: `patch_id`; `group` (`benchmark`, `hospital 4`, or `hospital 5`);
  `hospital` (1 to 5); `slide_id` (patches from one slide share it); `label` (1 if the
  center of the patch contains tumor); `p_tumor` (the model's probability of tumor);
  `predicted_tumor` (1 if `p_tumor` is at least 0.5).
- `release_summary.json`: counts, accuracies, the pinned source revision, and the seed.

## The model

ImageNet ResNet-18 features followed by logistic regression, fitted on other slides from
hospitals 1, 2, and 3. Those fitting patches are not included. The `benchmark` patches come
from held-out slides of hospitals 1 to 3; hospitals 4 and 5 were never seen by the model.

## Sampling

This is a small teaching subset, not a probability sample. Hospitals 4 and 5 each have
150 tumor and 150 non-tumor patches. The benchmark is about 55% tumor overall, but its
hospitals differ: about 78% tumor at hospital 1, 63% at hospital 2, and 24% at hospital 3.
Either way, the share of tumor patches does not match a real slide, where most tissue is
not tumor. Patches from one slide are related, so resample slides, not patches, for
intervals.

## Source and license

Camelyon17-WILDS (Koh et al. 2021, "WILDS: A Benchmark of in-the-Wild Distribution
Shifts"), built from the CAMELYON17 challenge (Bandi et al. 2019). WILDS lists the dataset
as public domain under CC0. Downloaded from the Hugging Face mirror
`wltjr1007/Camelyon17-WILDS` at a pinned revision (see `release_summary.json`).
"""


if __name__ == "__main__":
    main()
