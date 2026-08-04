"""Create small deterministic fixtures that exercise every course data contract.

These are pipeline-test fixtures, not release teaching data and not substitutes for
the documented source datasets. They allow clean-runtime execution before the
licensed/frozen teaching subsets are finalized.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "smoke"
RNG = np.random.default_rng(2027)


def logistic(x):
    return 1 / (1 + np.exp(-x))


def camera_traps() -> dict:
    root = OUT / "camera_traps"
    images = root / "images"
    images.mkdir(parents=True, exist_ok=True)
    metadata, features, outputs, splits = [], [], [], []
    image_number = 0
    for camera in range(16):
        split = "analysis" if camera < 12 else ("holdout_camera" if camera < 14 else "homework_holdout")
        camera_effect = RNG.normal(0, 0.7)
        # Keep the synthetic homework cameras moderately balanced. The fixture
        # must exercise the error-gallery path for both systems; an earlier draw
        # happened to make the fitted baseline perfect on all 30 homework rows.
        if camera >= 14:
            camera_effect = 0.0
        for sequence in range(5):
            sequence_id = f"cam{camera:02d}_seq{sequence:02d}"
            night = int(RNG.random() < 0.42)
            animal = int(RNG.random() < logistic(-0.2 + camera_effect - 0.35 * night))
            sequence_texture = RNG.normal(0, 0.12)
            for frame in range(3):
                image_number += 1
                image_id = f"img{image_number:04d}"
                brightness = np.clip(0.68 - 0.45 * night + 0.08 * animal + RNG.normal(0, 0.08), 0, 1)
                edge_signal = 0.25 if camera >= 14 else 0.35
                edge_density = np.clip(0.22 + edge_signal * animal + sequence_texture + RNG.normal(0, 0.06), 0, 1)
                green_fraction = np.clip(0.48 - 0.10 * night + RNG.normal(0, 0.12), 0, 1)
                vision_prob = np.clip(logistic(-1.1 + 3.7 * edge_density + 0.8 * brightness - 0.4 * night + RNG.normal(0, 0.5)), 0.01, 0.99)
                path = images / f"{image_id}.png"
                base = np.zeros((32, 32, 3))
                base[..., 0] = brightness * (0.75 if night else 1.0)
                base[..., 1] = green_fraction
                base[..., 2] = 0.25 + 0.35 * night
                if animal:
                    base[10:22, 8 + frame:24 + frame, :] = [0.85, 0.66, 0.32]
                base += RNG.normal(0, 0.035, base.shape)
                plt.imsave(path, np.clip(base, 0, 1))
                metadata.append(
                    {
                        "image_id": image_id,
                        "camera_id": f"cam{camera:02d}",
                        "sequence_id": sequence_id,
                        "frame_index": frame,
                        "day_night": "night" if night else "day",
                        "animal_present": animal,
                        "image_path": str(path.relative_to(OUT)),
                        "smoke_fixture": True,
                    }
                )
                features.append(
                    {
                        "image_id": image_id,
                        "brightness": brightness,
                        "edge_density": edge_density,
                        "green_fraction": green_fraction,
                        "night_indicator": night,
                    }
                )
                outputs.append(
                    {
                        "image_id": image_id,
                        "vision_prob": vision_prob,
                        "vision_pred": int(vision_prob >= 0.5),
                    }
                )
                splits.append({"image_id": image_id, "split": split})
    pd.DataFrame(metadata).to_csv(root / "metadata.csv", index=False)
    pd.DataFrame(features).to_csv(root / "image_features.csv", index=False)
    pd.DataFrame(outputs).to_csv(root / "model_outputs.csv", index=False)
    pd.DataFrame(splits).to_csv(root / "splits.csv", index=False)
    merged = pd.DataFrame(metadata).merge(pd.DataFrame(outputs), on="image_id")
    merged.to_csv(root / "homework_outputs.csv", index=False)
    return {"rows": len(metadata), "sequences": len(set(row["sequence_id"] for row in metadata))}


def cfpb() -> dict:
    root = OUT / "cfpb"
    root.mkdir(parents=True, exist_ok=True)
    products = ["Credit card", "Debt collection", "Credit reporting"]
    issues = {
        "Credit card": ["Billing dispute", "Fees"],
        "Debt collection": ["Not owed", "Harassment"],
        "Credit reporting": ["Incorrect information", "Identity theft"],
    }
    channels = ["Web", "Phone", "Referral"]
    narrative_bits = {
        "Credit card": "I disputed a card charge and the bank did not resolve the billing problem",
        "Debt collection": "A collector contacted me about a debt that I do not recognize",
        "Credit reporting": "My credit report contains information that does not belong to me",
    }
    rows = []
    for i in range(180):
        period = "source" if i < 110 else "target"
        weights = [0.46, 0.34, 0.20] if period == "source" else [0.27, 0.28, 0.45]
        product = RNG.choice(products, p=weights)
        issue = RNG.choice(issues[product])
        duplicate = bool(i % 23 == 0)
        narrative = narrative_bits[product]
        if issue in {"Fees", "Harassment", "Identity theft"}:
            narrative += f". The specific issue was {issue.lower()}"
        narrative += f". Reference detail {i % 17}."
        if duplicate:
            narrative = "Template complaint: " + narrative_bits[product] + "."
        rows.append(
            {
                "complaint_id": f"c{i:04d}",
                "narrative": narrative,
                "product": product,
                "issue": issue,
                "date_received": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i * 3),
                "submitted_via": RNG.choice(channels, p=[0.72, 0.18, 0.10]),
                "consumer_consent_provided": bool(RNG.random() < 0.78),
                "similarity_group": f"template_{i % 4}" if duplicate else f"unique_{i}",
                "duplicate_flag": duplicate,
                "period": period,
            }
        )
    complaints = pd.DataFrame(rows)
    complaints["n_words"] = complaints["narrative"].str.split().str.len()
    complaints.to_csv(root / "complaints.csv", index=False)

    label_map = {product: index for index, product in enumerate(products)}
    y = complaints["product"].map(label_map).to_numpy()
    baseline_correct = RNG.random(len(y)) < np.where(complaints["period"].eq("source"), 0.76, 0.68)
    ai_correct = RNG.random(len(y)) < np.where(complaints["period"].eq("source"), 0.82, 0.75)
    baseline_pred = np.where(baseline_correct, y, (y + RNG.integers(1, 3, len(y))) % 3)
    ai_pred = np.where(ai_correct, y, (y + RNG.integers(1, 3, len(y))) % 3)
    model = complaints[["complaint_id", "narrative", "product", "issue", "period", "duplicate_flag"]].copy()
    model["true_label"] = y
    model["baseline_pred"] = baseline_pred
    model["ai_pred"] = ai_pred
    model["baseline_correct"] = baseline_correct
    model["ai_correct"] = ai_correct
    model["baseline_correct_collapsed"] = baseline_correct | (RNG.random(len(y)) < 0.04)
    model["ai_correct_collapsed"] = ai_correct | (RNG.random(len(y)) < 0.03)
    model["baseline_confidence"] = np.clip(RNG.normal(np.where(baseline_correct, 0.73, 0.57), 0.12), 0.34, 0.99)
    model["ai_confidence"] = np.clip(RNG.normal(np.where(ai_correct, 0.86, 0.79), 0.10), 0.34, 0.99)
    model["correct"] = model["ai_correct"]
    model.to_csv(root / "model_outputs.csv", index=False)
    model.loc[model["period"].eq("target")].to_csv(root / "future_holdout_outputs.csv", index=False)
    (root / "weak_analysis_plan.txt").write_text(
        "Randomly split all complaints, try several category groupings, tune the transformer, "
        "and report whichever accuracy and subgroup results are best. If the transformer wins, deploy it.\n"
    )
    return {"rows": len(complaints), "target_rows": int(complaints["period"].eq("target").sum())}


def dynasent() -> dict:
    root = OUT / "dynasent"
    root.mkdir(parents=True, exist_ok=True)
    texts = [
        "The service was quick, although the result was disappointing.",
        "I expected worse and somehow got exactly that.",
        "The update works, but I miss the old design.",
        "Nothing special happened and everything was fine.",
        "An ambitious idea with an uneven execution.",
        "I cannot decide whether I loved it or hated it.",
    ]
    rows = []
    # Build disjoint lab and homework subsets. Each contains both natural
    # Round 1 and model-in-the-loop Round 2 rows so the complete Week 2 path can
    # execute without leaking the homework items during lab.
    for i in range(144):
        dominant = i % 3
        pattern = [5, 0, 0] if i % 5 == 0 else ([4, 1, 0] if i % 2 == 0 else [3, 2, 0])
        counts = np.roll(pattern, dominant)
        raw = RNG.dirichlet(np.array(counts) + 1)
        rows.append(
            {
                "item_id": f"d{i:03d}",
                "sentence": texts[i % len(texts)] + f" Item {i}.",
                "collection_round": 1 if (i % 72) < 36 else 2,
                "negative_votes": int(counts[0]),
                "neutral_votes": int(counts[1]),
                "positive_votes": int(counts[2]),
                "model_p_negative": raw[0],
                "model_p_neutral": raw[1],
                "model_p_positive": raw[2],
                "model_label": ["negative", "neutral", "positive"][int(raw.argmax())],
            }
        )
    lab_rows = rows[:72]
    homework_rows = rows[72:]
    pd.DataFrame(lab_rows).to_csv(root / "items.csv", index=False)
    pd.DataFrame(homework_rows).to_csv(root / "homework_items.csv", index=False)
    pd.DataFrame(homework_rows[:6]).to_csv(root / "prompt_items.csv", index=False)
    return {
        "rows": len(rows),
        "lab_rows": len(lab_rows),
        "homework_rows": len(homework_rows),
        "prompt_rows": 6,
        "raters_per_item": 5,
    }


def nhanes() -> dict:
    root = OUT / "nhanes"
    root.mkdir(parents=True, exist_ok=True)
    n = 140
    age = RNG.integers(18, 80, n)
    weight = RNG.uniform(0.4, 3.0, n)
    bp1 = 105 + 0.42 * age + RNG.normal(0, 10, n)
    bp2 = bp1 + RNG.normal(-1.5, 5, n)
    data = pd.DataFrame({"participant_id": np.arange(n), "age": age, "survey_weight": weight, "systolic_1": bp1, "systolic_2": bp2})
    data.to_csv(root / "blood_pressure.csv", index=False)
    return {"rows": n}


def designed_eval() -> dict:
    root = OUT / "designed_eval"
    root.mkdir(parents=True, exist_ok=True)
    pairs, orders, judgments = [], [], []
    protocols = ["minimal", "rubric", "order_blinded"]
    families = ["reasoning", "writing", "coding", "advice"]
    for i in range(48):
        pair_id = f"p{i:03d}"
        family = families[i % len(families)]
        reference = "A" if RNG.random() < 0.5 else "B"
        response_a = f"Response A to {family} prompt {i}: concise answer with evidence {i % 7}."
        response_b = f"Response B to {family} prompt {i}: longer stylistic answer with caveat {i % 5}."
        pairs.append({"pair_id": pair_id, "prompt_family": family, "response_a": response_a, "response_b": response_b, "human_preference": reference})
        ab_choice = reference if RNG.random() < 0.74 else ("B" if reference == "A" else "A")
        flips = RNG.random() < 0.18
        ba_choice = ("B" if ab_choice == "A" else "A") if flips else ab_choice
        orders.append(
            {
                "pair_id": pair_id,
                "prompt_family": family,
                "initial_order": "AB" if i % 2 == 0 else "BA",
                "human_preference": reference,
                "ab_choice": ab_choice,
                "ba_choice": ba_choice,
                "repeat_consistency": float(np.clip(RNG.normal(0.84, 0.12), 0, 1)),
            }
        )
        for protocol in protocols:
            agreement_prob = {"minimal": 0.68, "rubric": 0.78, "order_blinded": 0.75}[protocol]
            agrees = RNG.random() < agreement_prob
            choice = reference if agrees else ("B" if reference == "A" else "A")
            judgments.append(
                {
                    "pair_id": pair_id,
                    "prompt_family": family,
                    "protocol": protocol,
                    "judge_choice": choice,
                    "agrees_with_reference": agrees,
                    "repeat_consistent": RNG.random() < (0.80 if protocol == "minimal" else 0.88),
                    "order_reversed": RNG.random() < (0.20 if protocol == "minimal" else 0.12),
                }
            )
    pd.DataFrame(pairs).to_csv(root / "response_pairs.csv", index=False)
    pd.DataFrame(orders).to_csv(root / "order_experiment.csv", index=False)
    pd.DataFrame(judgments).to_csv(root / "llm_judge_prompt_variants.csv", index=False)
    return {"pairs": len(pairs), "judgment_rows": len(judgments)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "bundle_type": "deterministic smoke fixture — never release as source data",
        "seed": 2027,
        "camera_traps": camera_traps(),
        "cfpb": cfpb(),
        "dynasent": dynasent(),
        "nhanes": nhanes(),
        "designed_eval": designed_eval(),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
