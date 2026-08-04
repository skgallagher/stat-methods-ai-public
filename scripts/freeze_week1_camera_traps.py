"""Freeze the licensed Caltech Camera Traps subset used in Week 1.

The release is intentionally small enough for direct per-file GitHub downloads.
It samples complete three-frame sequences, keeps cameras disjoint across the
analysis/lab/homework splits, computes the documented transparent features, and
uses the official LILA MegaDetector v5a RDE output as the supplied vision score.
"""

from __future__ import annotations

import argparse
import io
import json
import time
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.linear_model import LogisticRegression


IMAGE_BASE_URL = (
    "https://lilawildlife.blob.core.windows.net/lila-wildlife/"
    "caltech-unzipped/cct_images"
)
ALLOWED_SPLITS = ("analysis", "holdout_camera", "homework_holdout")


def load_source_records(annotation_path: Path, detector_path: Path) -> pd.DataFrame:
    annotations = json.loads(annotation_path.read_text())
    detector = json.loads(detector_path.read_text())
    category_names = {item["id"]: item["name"] for item in annotations["categories"]}

    image_categories: dict[str, list[str]] = defaultdict(list)
    for item in annotations["annotations"]:
        image_categories[item["image_id"]].append(category_names[item["category_id"]])

    detector_scores = {}
    for item in detector["images"]:
        animal_scores = [
            float(detection["conf"])
            for detection in item.get("detections", [])
            if detection.get("category") == "1"
        ]
        detector_scores[item["file"]] = max(animal_scores, default=0.0)

    rows = []
    for image in annotations["images"]:
        categories = sorted(set(image_categories.get(image["id"], ["empty"])))
        if "car" in categories:
            continue
        nonempty = [name for name in categories if name != "empty"]
        try:
            captured = datetime.strptime(image["date_captured"], "%Y-%m-%d %H:%M:%S")
        except (KeyError, TypeError, ValueError):
            # A small number of source records contain malformed timestamps and
            # cannot support the documented day/night feature.
            continue
        rows.append(
            {
                "source_image_id": image["id"],
                "source_file_name": image["file_name"],
                "camera_id": f"cct_location_{int(image['location']):03d}",
                "sequence_id": image["seq_id"],
                "frame_index": int(image["frame_num"]) - 1,
                "seq_num_frames": int(image["seq_num_frames"]),
                "date_captured": image["date_captured"],
                "day_night": "night" if captured.hour < 6 or captured.hour >= 18 else "day",
                "animal_present": int(bool(nonempty)),
                "species_label": "+".join(nonempty) if nonempty else "empty",
                "rights_holder": image.get("rights_holder", ""),
                "vision_prob": float(detector_scores.get(image["file_name"], 0.0)),
            }
        )
    return pd.DataFrame(rows)


def eligible_sequences(records: pd.DataFrame) -> dict[str, dict[int, list[str]]]:
    by_camera: dict[str, dict[int, list[str]]] = defaultdict(lambda: {0: [], 1: []})
    for sequence_id, sequence in records.groupby("sequence_id"):
        if len(sequence) != 3 or not sequence["seq_num_frames"].eq(3).all():
            continue
        if sorted(sequence["frame_index"].tolist()) != [0, 1, 2]:
            continue
        if sequence["camera_id"].nunique() != 1 or sequence["animal_present"].nunique() != 1:
            continue
        camera = sequence["camera_id"].iloc[0]
        label = int(sequence["animal_present"].iloc[0])
        by_camera[camera][label].append(sequence_id)
    return by_camera


def select_records(
    records: pd.DataFrame,
    *,
    seed: int,
    sequences_per_class: int,
) -> tuple[pd.DataFrame, int]:
    candidates = eligible_sequences(records)
    cameras = sorted(
        camera
        for camera, groups in candidates.items()
        if len(groups[0]) >= sequences_per_class and len(groups[1]) >= sequences_per_class
    )
    if len(cameras) < 12:
        raise ValueError(f"Need 12 eligible cameras; found {len(cameras)}")

    for attempt in range(10_000):
        rng = np.random.default_rng(seed + attempt)
        chosen_cameras = rng.choice(cameras, size=12, replace=False).tolist()
        assignments = {
            **{camera: "analysis" for camera in chosen_cameras[:6]},
            **{camera: "holdout_camera" for camera in chosen_cameras[6:9]},
            **{camera: "homework_holdout" for camera in chosen_cameras[9:12]},
        }
        chosen_sequences = []
        for camera in chosen_cameras:
            for label in (0, 1):
                sequence_ids = sorted(candidates[camera][label])
                selected = rng.choice(
                    sequence_ids, size=sequences_per_class, replace=False
                ).tolist()
                chosen_sequences.extend(selected)
        selected = records.loc[records["sequence_id"].isin(chosen_sequences)].copy()
        selected["split"] = selected["camera_id"].map(assignments)
        selected["vision_pred"] = (selected["vision_prob"] >= 0.5).astype(int)

        acceptable = True
        for split in ("holdout_camera", "homework_holdout"):
            evaluation = selected.loc[selected["split"].eq(split)]
            vision_errors = evaluation["vision_pred"].ne(evaluation["animal_present"]).sum()
            night_fraction = evaluation["day_night"].eq("night").mean()
            if vision_errors < 2 or not (0.05 <= night_fraction <= 0.95):
                acceptable = False
        if acceptable:
            selected = selected.sort_values(
                ["split", "camera_id", "sequence_id", "frame_index"]
            ).reset_index(drop=True)
            selected["image_id"] = [f"cct{index:04d}" for index in range(1, len(selected) + 1)]
            return selected, seed + attempt
    raise RuntimeError("No camera-disjoint selection satisfied the release checks")


def fetch_bytes(url: str, attempts: int = 4) -> bytes:
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                return response.read()
        except Exception:
            if attempt + 1 == attempts:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def image_features(image: Image.Image) -> dict[str, float]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    horizontal = np.abs(np.diff(gray, axis=1)).mean()
    vertical = np.abs(np.diff(gray, axis=0)).mean()
    channel_total = rgb.sum(axis=2)
    green_fraction = np.divide(
        rgb[:, :, 1], channel_total, out=np.zeros_like(channel_total), where=channel_total > 0
    ).mean()
    return {
        "brightness": float(gray.mean()),
        "edge_density": float((horizontal + vertical) / 2),
        "green_fraction": float(green_fraction),
    }


def write_release(selected: pd.DataFrame, output_root: Path, max_side: int) -> None:
    image_root = output_root / "images"
    image_root.mkdir(parents=True, exist_ok=True)
    feature_rows = []
    for number, row in enumerate(selected.itertuples(index=False), start=1):
        source_url = f"{IMAGE_BASE_URL}/{row.source_file_name}"
        raw = fetch_bytes(source_url)
        with Image.open(io.BytesIO(raw)) as source_image:
            image = source_image.convert("RGB")
            image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            destination = image_root / f"{row.image_id}.jpg"
            image.save(destination, format="JPEG", quality=82, optimize=True)
            computed = image_features(image)
        feature_rows.append(
            {
                "image_id": row.image_id,
                **computed,
                "night_indicator": int(row.day_night == "night"),
            }
        )
        if number % 25 == 0 or number == len(selected):
            print(f"downloaded and processed {number}/{len(selected)} images", flush=True)

    metadata = selected[
        [
            "image_id",
            "camera_id",
            "sequence_id",
            "frame_index",
            "day_night",
            "animal_present",
            "source_image_id",
            "source_file_name",
            "species_label",
            "date_captured",
            "rights_holder",
        ]
    ].copy()
    metadata["image_path"] = metadata["image_id"].map(
        lambda image_id: f"camera_traps/images/{image_id}.jpg"
    )
    metadata = metadata[
        [
            "image_id",
            "camera_id",
            "sequence_id",
            "frame_index",
            "day_night",
            "animal_present",
            "image_path",
            "source_image_id",
            "source_file_name",
            "species_label",
            "date_captured",
            "rights_holder",
        ]
    ]
    metadata.to_csv(output_root / "metadata.csv", index=False)
    pd.DataFrame(feature_rows).to_csv(output_root / "image_features.csv", index=False)
    selected[["image_id", "vision_prob", "vision_pred"]].assign(
        vision_model="MegaDetector v5a.0.0 with repeat-detection elimination"
    ).to_csv(output_root / "model_outputs.csv", index=False)
    selected[["image_id", "split"]].to_csv(output_root / "splits.csv", index=False)


def validate_release(output_root: Path, selection_seed: int) -> dict:
    data = (
        pd.read_csv(output_root / "metadata.csv")
        .merge(pd.read_csv(output_root / "image_features.csv"), on="image_id")
        .merge(pd.read_csv(output_root / "model_outputs.csv"), on="image_id")
        .merge(pd.read_csv(output_root / "splits.csv"), on="image_id")
    )
    assert set(data["split"]) == set(ALLOWED_SPLITS)
    assert data.groupby("camera_id")["split"].nunique().max() == 1
    assert data.groupby("sequence_id")["split"].nunique().max() == 1
    assert data.groupby("sequence_id").size().eq(3).all()
    assert data["image_id"].is_unique
    assert data["image_path"].map(lambda value: (output_root.parent / value).exists()).all()

    features = ["brightness", "edge_density", "green_fraction", "night_indicator"]
    analysis = data.query("split == 'analysis'")
    baseline = LogisticRegression(max_iter=2000).fit(
        analysis[features], analysis["animal_present"]
    )
    summary = {
        "selection_seed": selection_seed,
        "n_images": int(len(data)),
        "n_sequences": int(data["sequence_id"].nunique()),
        "n_cameras": int(data["camera_id"].nunique()),
        "source": "Caltech Camera Traps via LILA BC",
        "license": "Community Data License Agreement—Permissive",
        "vision_model": "MegaDetector v5a.0.0 with repeat-detection elimination",
        "warning": (
            "This fixed teaching subset is not a probability sample of all Caltech "
            "Camera Traps images or all wildlife cameras. MegaDetector training used "
            "Caltech Camera Traps, so its score is illustrative rather than an "
            "unbiased external benchmark."
        ),
        "splits": {},
    }
    for split in ALLOWED_SPLITS:
        subset = data.query("split == @split").copy()
        subset["baseline_pred"] = baseline.predict(subset[features])
        split_summary = {
            "n_images": int(len(subset)),
            "n_sequences": int(subset["sequence_id"].nunique()),
            "n_cameras": int(subset["camera_id"].nunique()),
            "animal_fraction": float(subset["animal_present"].mean()),
            "night_fraction": float(subset["night_indicator"].mean()),
            "baseline_accuracy": float(subset["baseline_pred"].eq(subset["animal_present"]).mean()),
            "vision_accuracy": float(subset["vision_pred"].eq(subset["animal_present"]).mean()),
            "baseline_errors": int(subset["baseline_pred"].ne(subset["animal_present"]).sum()),
            "vision_errors": int(subset["vision_pred"].ne(subset["animal_present"]).sum()),
        }
        if split != "analysis":
            assert split_summary["baseline_errors"] >= 2
            assert split_summary["vision_errors"] >= 2
        summary["splits"][split] = split_summary
    (output_root / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def write_readme(output_root: Path) -> None:
    readme = """# Week 1 Camera Traps teaching subset

This is a fixed, camera-disjoint teaching subset of **Caltech Camera Traps**, distributed by
[LILA BC](https://lila.science/datasets/caltech-camera-traps) under the Community Data
License Agreement—Permissive. Original image IDs, filenames, timestamps, labels, locations,
and rights holders are retained in `metadata.csv` for provenance.

The supplied AI score is the maximum animal-detection confidence from **MegaDetector
v5a.0.0 with repeat-detection elimination**, obtained from LILA BC's published results.
Caltech Camera Traps contributed to MegaDetector training; therefore this course comparison
is an illustration of evaluation structure, not an unbiased external benchmark of the model.

The subset contains complete three-frame trigger sequences. Camera locations are disjoint
across `analysis`, `holdout_camera`, and `homework_holdout`. Images are resized to at most
640 pixels on a side for direct individual-file download from GitHub.

The subset is deliberately small and balanced for teaching. It is not a probability sample
of all Caltech Camera Traps images, camera locations, ecosystems, or wildlife cameras.
See `release_summary.json` for frozen denominators and descriptive results.
"""
    (output_root / "README.md").write_text(readme)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--detector-results", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=2027)
    parser.add_argument("--sequences-per-class", type=int, default=3)
    parser.add_argument("--max-side", type=int, default=640)
    args = parser.parse_args()

    records = load_source_records(args.annotations, args.detector_results)
    selected, selection_seed = select_records(
        records,
        seed=args.seed,
        sequences_per_class=args.sequences_per_class,
    )
    args.output_root.mkdir(parents=True, exist_ok=True)
    write_release(selected, args.output_root, args.max_side)
    write_readme(args.output_root)
    summary = validate_release(args.output_root, selection_seed)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
