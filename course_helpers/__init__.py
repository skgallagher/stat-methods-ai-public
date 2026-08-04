"""Small, transparent helpers used by the Stat-AI labs and homeworks.

These functions intentionally expose the statistical unit and estimand. They are
teaching utilities, not a general machine-learning framework.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.request
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd


LABELS = ("negative", "neutral", "positive")


def get_data_root(default: str | Path | None = None) -> Path:
    """Return the configured course-data root without silently downloading data."""
    configured = os.environ.get("STAT_AI_DATA_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    if default is not None:
        return Path(default).expanduser().resolve()
    local = Path(__file__).resolve().parents[1] / "data" / "smoke"
    return local


def ensure_course_data(
    base_url: str,
    destination: str | Path = "/content/stat_ai_data",
    *,
    groups: Iterable[str] | None = None,
    overwrite: bool = False,
) -> Path:
    """Download selected release files directly from the public GitHub repository.

    ``base_url`` points to a directory containing ``manifest.json`` and the
    listed files. The manifest must declare ``release_status=student_release``;
    this prevents the synthetic smoke fixture from being distributed as course
    data. Existing files with matching hashes are reused.
    """
    if not base_url or "TBD_BEFORE_RELEASE" in base_url:
        raise ValueError("The public course-data URL has not been configured.")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    base_url = base_url.rstrip("/")
    with urllib.request.urlopen(f"{base_url}/manifest.json") as response:
        manifest_bytes = response.read()
    release = json.loads(manifest_bytes)
    if release.get("release_status") != "student_release":
        raise ValueError("Refusing data that are not marked as a student release.")
    files = release.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Course-data manifest has no files.")

    selected_groups = set(groups or [])
    available_groups = {Path(item["path"]).parts[0] for item in files}
    missing_groups = selected_groups - available_groups
    if missing_groups:
        raise ValueError(f"Groups missing from course-data release: {sorted(missing_groups)}")

    def digest(path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    for item in files:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe course-data path: {relative}")
        if selected_groups and relative.parts[0] not in selected_groups:
            continue
        expected_hash = item["sha256"]
        target = destination / relative
        if target.exists() and not overwrite and digest(target) == expected_hash:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(target.suffix + ".part")
        urllib.request.urlretrieve(f"{base_url}/{relative.as_posix()}", partial)
        actual_hash = digest(partial)
        if actual_hash != expected_hash:
            partial.unlink(missing_ok=True)
            raise ValueError(f"Hash mismatch for {relative}")
        partial.replace(target)

    (destination / "manifest.json").write_bytes(manifest_bytes)
    return destination


def expand_dynasent_raters(items: pd.DataFrame) -> pd.DataFrame:
    """Expand one DynaSent item per row into one row per item–rater judgment.

    Accepted inputs contain either ``negative_votes``/``neutral_votes``/
    ``positive_votes`` or a JSON/dict ``label_distribution`` column.
    """
    required = {"item_id"}
    if not required.issubset(items):
        raise ValueError("items must contain item_id")
    rows: list[dict] = []
    for item in items.to_dict("records"):
        if all(f"{label}_votes" in item for label in LABELS):
            counts = {label: int(item[f"{label}_votes"]) for label in LABELS}
        elif "label_distribution" in item:
            value = item["label_distribution"]
            counts = json.loads(value) if isinstance(value, str) else dict(value)
            counts = {label: int(counts.get(label, 0)) for label in LABELS}
        else:
            raise ValueError("items need vote-count columns or label_distribution")
        rater = 0
        for label in LABELS:
            for _ in range(counts[label]):
                rater += 1
                rows.append({"item_id": item["item_id"], "rater_index": rater, "label": label})
    return pd.DataFrame(rows)


def summarize_votes(ratings: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    """Create rater proportions, majority label, vote pattern, and scores."""
    counts = (
        ratings.groupby(["item_id", "label"]).size().unstack(fill_value=0)
        .reindex(columns=LABELS, fill_value=0)
    )
    totals = counts.sum(axis=1)
    proportions = counts.div(totals, axis=0).add_prefix("p_")
    summary = proportions.copy()
    summary["n_raters"] = totals
    summary["majority_label"] = counts.idxmax(axis=1)
    ordered = np.sort(counts.to_numpy(), axis=1)[:, ::-1]
    summary["vote_pattern"] = [f"{row[0]}-{row[1]}" for row in ordered]
    summary = summary.reset_index().merge(items, on="item_id", how="left")
    if "model_label" in summary:
        summary["model_correct_majority"] = summary["model_label"].eq(summary["majority_label"])
    probability_columns = [f"model_p_{label}" for label in LABELS]
    if set(probability_columns).issubset(summary):
        p = summary[probability_columns].to_numpy(float)
        y_soft = summary[[f"p_{label}" for label in LABELS]].to_numpy(float)
        summary["soft_brier"] = ((p - y_soft) ** 2).sum(axis=1)
    return summary


def wilson_interval(successes: int, total: int, level: float = 0.95) -> tuple[float, float]:
    """Wilson interval for a binomial proportion (95% only in course use)."""
    if total <= 0:
        return (np.nan, np.nan)
    if not np.isclose(level, 0.95):
        raise ValueError("This transparent course helper currently supports level=.95")
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    radius = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    return center - radius, center + radius


def sequence_bootstrap(
    data: pd.DataFrame,
    statistic: Callable[[pd.DataFrame], float],
    *,
    unit_col: str = "sequence_id",
    B: int = 2000,
    seed: int = 2027,
) -> np.ndarray:
    """Percentile bootstrap that resamples complete units, never individual rows."""
    if unit_col not in data:
        raise ValueError(f"missing resampling unit {unit_col}")
    units = data[unit_col].drop_duplicates().to_numpy()
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(B):
        sampled_units = rng.choice(units, len(units), replace=True)
        sampled = pd.concat([data.loc[data[unit_col].eq(unit)] for unit in sampled_units])
        estimates.append(statistic(sampled))
    return np.quantile(estimates, [0.025, 0.975])


def paired_bootstrap_interval(
    data: pd.DataFrame,
    *,
    baseline_col: str = "baseline_correct",
    ai_col: str = "ai_correct",
    unit_col: str | None = None,
    B: int = 2000,
    seed: int = 2027,
) -> tuple[float, tuple[float, float]]:
    """Paired difference and bootstrap interval, resampling shared rows or units."""
    if unit_col is None:
        units = np.arange(len(data))
        groups = {unit: data.iloc[[unit]] for unit in units}
    else:
        units = data[unit_col].drop_duplicates().to_numpy()
        groups = {unit: data.loc[data[unit_col].eq(unit)] for unit in units}
    estimate = float(data[ai_col].mean() - data[baseline_col].mean())
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B):
        sampled_units = rng.choice(units, len(units), replace=True)
        sampled = pd.concat([groups[unit] for unit in sampled_units])
        draws.append(sampled[ai_col].mean() - sampled[baseline_col].mean())
    interval = tuple(np.quantile(draws, [0.025, 0.975]))
    return estimate, interval


def compare_populations(source: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """A compact, denominator-visible CFPB source/target comparison."""
    records = [
        {"quantity": "n", "level": "all", "source": len(source), "target": len(target)},
        {
            "quantity": "mean_n_words",
            "level": "all",
            "source": source["n_words"].mean(),
            "target": target["n_words"].mean(),
        },
    ]
    for column in ["product", "submitted_via"]:
        if column not in source or column not in target:
            continue
        levels = sorted(set(source[column].dropna()) | set(target[column].dropna()))
        for level in levels:
            records.append(
                {
                    "quantity": f"proportion_{column}",
                    "level": level,
                    "source": source[column].eq(level).mean(),
                    "target": target[column].eq(level).mean(),
                }
            )
    result = pd.DataFrame(records)
    result["difference_target_minus_source"] = result["target"] - result["source"]
    return result


def fit_domain_classifier(
    source: pd.DataFrame,
    target: pd.DataFrame,
    *,
    text_col: str = "narrative",
    seed: int = 2027,
) -> dict:
    """Cross-validated TF–IDF logistic classifier for source versus target."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline

    combined = pd.concat(
        [source.assign(_domain=0), target.assign(_domain=1)], ignore_index=True
    )
    model = make_pipeline(
        TfidfVectorizer(min_df=1, max_features=1000),
        LogisticRegression(max_iter=2000),
    )
    folds = min(5, int(combined["_domain"].value_counts().min()))
    cv = StratifiedKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    scores = cross_val_score(model, combined[text_col].fillna(""), combined["_domain"], cv=cv)
    floor = combined["_domain"].value_counts(normalize=True).max()
    return {"cv_accuracy": scores.mean(), "fold_scores": scores, "majority_floor": floor}


def run_cfpb_specification(
    specification: str,
    data: pd.DataFrame | None = None,
    *,
    practical_threshold: float = 0.03,
) -> dict:
    """Run one locked CFPB comparison used in the sensitivity lab."""
    if data is None:
        data = pd.read_csv(get_data_root() / "cfpb" / "future_holdout_outputs.csv")
    analysis = data.copy()
    if specification == "exclude_duplicates":
        analysis = analysis.loc[~analysis["duplicate_flag"].astype(bool)].copy()
    elif specification == "target_period_only":
        analysis = analysis.loc[analysis["period"].eq("target")].copy()
    elif specification == "collapsed_labels":
        # Cached predictions include correctness under the released collapsed rule.
        analysis["baseline_correct"] = analysis["baseline_correct_collapsed"]
        analysis["ai_correct"] = analysis["ai_correct_collapsed"]
    elif specification != "primary":
        raise ValueError(f"unknown locked specification: {specification}")
    estimate, interval = paired_bootstrap_interval(analysis, B=1000)
    return {
        "specification": specification,
        "analysis_population": specification.replace("_", " "),
        "n": len(analysis),
        "estimand": "AI minus baseline accuracy",
        "estimate": estimate,
        "lower": interval[0],
        "upper": interval[1],
        "decision": "prefer AI" if estimate >= practical_threshold else "no practical advantage",
    }


def paired_interval(primary: dict, alternative: dict) -> pd.DataFrame:
    """Place two locked specification results in the common sensitivity schema."""
    columns = [
        "specification", "analysis_population", "n", "estimand",
        "estimate", "lower", "upper", "decision",
    ]
    return pd.DataFrame([primary, alternative])[columns]


def judge_protocol_table(judgments: pd.DataFrame) -> pd.DataFrame:
    """Summarize LLM-judge protocols with response-pair denominators."""
    required = {
        "protocol", "pair_id", "agrees_with_reference",
        "repeat_consistent", "order_reversed",
    }
    if not required.issubset(judgments):
        raise ValueError(f"missing columns: {sorted(required - set(judgments))}")
    return (
        judgments.groupby("protocol")
        .agg(
            n_pairs=("pair_id", "nunique"),
            reference_agreement=("agrees_with_reference", "mean"),
            repeat_consistency=("repeat_consistent", "mean"),
            order_reversal_rate=("order_reversed", "mean"),
        )
        .reset_index()
    )


def copy_smoke_bundle(destination: str | Path = "/content/stat_ai_data") -> Path:
    """Copy repository smoke fixtures into a Colab-like data root for testing."""
    source = Path(__file__).resolve().parents[1] / "data" / "smoke"
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return destination
