"""Build seven student-facing Colab homework notebooks from the QMD prompts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from colab_data_setup import build_setup


ROOT = Path(__file__).resolve().parents[1]
HOMEWORKS = [
    ("week01", "hw01", "Homework 1"),
    ("week02", "hw02", "Homework 2"),
    ("week03", "hw03", "Homework 3"),
    ("week04", "hw04", "Homework 4"),
    ("week05", "hw05", "Homework 5"),
    ("week10", "hw06", "Homework 6"),
    ("week12", "hw07", "Homework 7"),
]

DATA_GROUPS = {
    "hw01": ["camera_traps"],
    "hw02": ["dynasent"],
    "hw03": ["cfpb"],
    "hw04": ["camera_traps", "nhanes"],
    "hw05": ["cfpb"],
    "hw06": ["cfpb"],
    "hw07": ["designed_eval"],
}

STARTER_LINES = {
    "hw01": [
        "# HW1: baseline fit and paired cases (Problem 1 is mathematical work)",
        "def sigmoid(z):",
        "    return 1 / (1 + np.exp(-z))",
        "# Problem 1: show your derivations in the response cells; no AI assistance.",
        "camera_root = DATA_ROOT / 'camera_traps'",
        "meta = pd.read_csv(camera_root / 'metadata.csv')",
        "features = pd.read_csv(camera_root / 'image_features.csv')",
        "outputs = pd.read_csv(camera_root / 'model_outputs.csv')",
        "splits = pd.read_csv(camera_root / 'splits.csv')",
        "camera = meta.merge(features, on='image_id').merge(outputs, on='image_id').merge(splits, on='image_id')",
        "FEATURES = ['brightness', 'edge_density', 'green_fraction', 'night_indicator']",
        "from sklearn.linear_model import LogisticRegression",
        "analysis = camera.query(\"split == 'analysis'\").copy()",
        "holdout = camera.query(\"split == 'homework_holdout'\").copy()",
        "assert set(analysis['camera_id']).isdisjoint(set(holdout['camera_id']))",
        "assert camera.groupby('sequence_id')['split'].nunique().max() == 1",
        "baseline = LogisticRegression(max_iter=2000).fit(analysis[FEATURES], analysis['animal_present'])",
        "for frame in [analysis, holdout]:",
        "    frame['baseline_prob'] = baseline.predict_proba(frame[FEATURES])[:, 1]",
        "    frame['baseline_pred'] = (frame['baseline_prob'] >= .5).astype(int)",
        "def paired_correctness_table(data):",
        "    paired = data.assign(",
        "        baseline_correct=data['baseline_pred'].eq(data['animal_present']),",
        "        ai_correct=data['vision_pred'].eq(data['animal_present']),",
        "    )",
        "    return (paired.groupby(['baseline_correct', 'ai_correct']).size()",
        "            .reindex(pd.MultiIndex.from_product(",
        "                [[True, False], [True, False]],",
        "                names=['baseline_correct', 'ai_correct']), fill_value=0)",
        "            .rename('n').reset_index())",
        "def select_system_errors(data, system, seed=SEED):",
        "    columns = {'baseline': ('baseline_prob', 'baseline_pred'),",
        "               'vision': ('vision_prob', 'vision_pred')}",
        "    prob_col, pred_col = columns[system]",
        "    errors = data.loc[data[pred_col].ne(data['animal_present'])].copy()",
        "    if len(errors) < 2:",
        "        raise ValueError(f'{system} needs at least two errors for the locked gallery')",
        "    errors['predicted_confidence'] = np.where(",
        "        errors[pred_col].eq(1), errors[prob_col], 1 - errors[prob_col])",
        "    errors = errors.sort_values(",
        "        ['predicted_confidence', 'image_id'], ascending=[False, True])",
        "    highest = errors.head(1).assign(selection_rule='highest confidence')",
        "    random_case = errors.iloc[1:].sample(n=1, random_state=seed).assign(",
        "        selection_rule='reproducibly random')",
        "    selected = pd.concat([random_case, highest], ignore_index=True)",
        "    selected['system'] = system",
        "    selected['model_probability'] = selected[prob_col]",
        "    selected['model_prediction'] = selected[pred_col]",
        "    return selected",
        "# TODO Problem 2: compute floors and accuracies, then call the paired-table",
        "# and locked-error helpers. Keep all requested output visible.",
    ],
    "hw02": [
        "# HW2: rater summaries, Brier targets, and prompt comparison",
        "from course_helpers import expand_dynasent_raters, summarize_votes",
        "LABELS = ['negative', 'neutral', 'positive']",
        "def multiclass_brier(prob, outcome):",
        "    prob, outcome = np.asarray(prob), np.asarray(outcome)",
        "    return np.sum((prob - outcome) ** 2)",
        "dynasent_root = DATA_ROOT / 'dynasent'",
        "homework_items = pd.read_csv(dynasent_root / 'homework_items.csv')",
        "prompt_items = pd.read_csv(dynasent_root / 'prompt_items.csv')",
        "ratings = expand_dynasent_raters(homework_items)",
        "rater_summary = summarize_votes(ratings, homework_items)",
        "assert ratings.groupby('item_id').size().eq(5).all()",
        "assert np.allclose(rater_summary[[f'p_{label}' for label in LABELS]].sum(axis=1), 1)",
        "# TODO Problem 1: construct one-hot majority targets and compare Brier scores.",
        "# TODO Problem 2: make denominator-first vote-pattern and round tables.",
        "prompt_comparison = pd.DataFrame(columns=[",
        "    'item_id', 'sentence', 'p_negative', 'p_neutral', 'p_positive',",
        "    'majority_label', 'prompt_a_label', 'prompt_b_label', 'changed'])",
        "prompt_comparison",
    ],
    "hw03": [
        "# HW3: design brief and workflow audit structures",
        "design_brief = {",
        "    'research_question': '', 'hypothesis': '',",
        "    'observed_population': '', 'target_population': '',",
        "    'observation_and_grouping_unit': '', 'primary_estimand': '',",
        "    'baseline_and_ai_system': '', 'analysis_validation_holdout_roles': '',",
        "    'metric_and_practical_difference': '', 'decision_informed': '',",
        "    'claim_not_supported': ''}",
        "workflow_audit = pd.DataFrame(columns=[",
        "    'step', 'action', 'information_used', 'threat',",
        "    'expected_direction', 'locked_repair'])",
        "plan_audit = pd.DataFrame(index=[",
        "    'target', 'unit/split', 'baseline', 'uncertainty', 'claim'],",
        "    columns=['weak_prompt_plan', 'specified_prompt_plan', 'your_evaluation'])",
    ],
    "hw04": [
        "# HW4: interval arithmetic and complete-sequence resampling",
        "from statsmodels.stats.proportion import proportion_confint",
        "x, n = 184, 200",
        "p_hat = x / n",
        "wald = (p_hat - 1.96*np.sqrt(p_hat*(1-p_hat)/n),",
        "        p_hat + 1.96*np.sqrt(p_hat*(1-p_hat)/n))",
        "wilson = proportion_confint(x, n, method='wilson')",
        "def sequence_bootstrap(data, statistic, B=2000, seed=2027):",
        "    rng = np.random.default_rng(seed)",
        "    ids = data['sequence_id'].unique()",
        "    estimates = []",
        "    for _ in range(B):",
        "        sampled_ids = rng.choice(ids, len(ids), replace=True)",
        "        sampled = pd.concat([data.query('sequence_id == @sid') for sid in sampled_ids])",
        "        estimates.append(statistic(sampled))",
        "    return np.quantile(estimates, [0.025, 0.975])",
        "# Problem 3 release files include ai_bootstrap_attempt.py and supplied_checks().",
    ],
    "hw05": [
        "# HW5: paired arithmetic and paired-row bootstrap",
        "both_correct, baseline_only, ai_only, both_wrong = 390, 35, 55, 20",
        "n_cases = both_correct + baseline_only + ai_only + both_wrong",
        "baseline_accuracy = (both_correct + baseline_only) / n_cases",
        "ai_accuracy = (both_correct + ai_only) / n_cases",
        "observed_difference = ai_accuracy - baseline_accuracy",
        "def paired_difference(data):",
        "    return data['ai_correct'].mean() - data['baseline_correct'].mean()",
        "def paired_bootstrap(data, B=2000, seed=2027):",
        "    rng = np.random.default_rng(seed)",
        "    estimates = []",
        "    for _ in range(B):",
        "        idx = rng.integers(0, len(data), len(data))",
        "        estimates.append(paired_difference(data.iloc[idx]))",
        "    return np.quantile(estimates, [0.025, 0.975])",
        "cfpb_root = DATA_ROOT / 'cfpb'",
    ],
    "hw06": [
        "# HW6: save the pre-specification before revealing held-back output",
        "prespecification = pd.DataFrame(columns=[",
        "    'alternative', 'assumption_varied', 'why_both_reasonable',",
        "    'expected_direction_or_unknown', 'decision_flip_rule',",
        "    'chosen_before_reveal'])",
        "prespecification",
        "# After saving Problem 1, reuse run_cfpb_specification() and paired_interval().",
        "ai_alternatives = pd.DataFrame(columns=[",
        "    'ai_suggestion', 'real_assumption_or_model_shopping',",
        "    'accept_or_reject', 'statistical_reason'])",
    ],
    "hw07": [
        "# HW7: paired agreement and pair-ID resampling",
        "both_agree, minimal_only, rubric_only, neither = 60, 10, 20, 10",
        "n_pairs = both_agree + minimal_only + rubric_only + neither",
        "minimal_agreement = (both_agree + minimal_only) / n_pairs",
        "rubric_agreement = (both_agree + rubric_only) / n_pairs",
        "observed_difference = rubric_agreement - minimal_agreement",
        "def bootstrap_pairs(data, statistic, B=2000, seed=2027):",
        "    rng = np.random.default_rng(seed)",
        "    pair_ids = data['pair_id'].drop_duplicates().to_numpy()",
        "    estimates = []",
        "    for _ in range(B):",
        "        sampled_ids = rng.choice(pair_ids, len(pair_ids), replace=True)",
        "        sampled = pd.concat([data.query('pair_id == @pid') for pid in sampled_ids])",
        "        estimates.append(statistic(sampled))",
        "    return np.quantile(estimates, [0.025, 0.975])",
        "judge_root = DATA_ROOT / 'designed_eval'",
        "run_order = np.random.default_rng(SEED).permutation(['minimal', 'rubric']).tolist()",
    ],
}

WORKFLOW = "\n".join([
    "## How to work in this notebook",
    "",
    "This `.ipynb` is your **only working document**. The assignment PDF is a read-only copy of the same prompt. Do not edit or combine a `.qmd` file.",
    "",
    "- Write reasoning in the designated text cells.",
    "- Run or modify the starter code rather than pasting an unexplained replacement.",
    "- Keep requested output, plots, excerpts, and raw AI evidence visible.",
    "- Handwriting is welcome but never required. Typed Markdown/LaTeX is fully equivalent.",
    "- If you insert a clear scan/photo, add one typed description or statistical conclusion for accessibility.",
    "",
    "Before submission, restart and run all. Upload a PDF export and the completed `.ipynb` to the same Gradescope assignment. If image insertion fails, add one clearly labeled optional handwriting PDF; do not merge files.",
])

RESPONSE = "\n".join([
    "### Your response — {label}",
    "",
    "Type your response here **or** insert a clear image of handwritten work here.",
    "",
    "**Prediction before assistance/output, when requested:**  ",
    "TODO or not applicable",
    "",
    "**Analysis, evidence, or reasoning:**  ",
    "TODO",
    "",
    "**Typed statistical conclusion (required even with handwriting):**  ",
    "TODO",
])

HW1_P3A_RESPONSE = "\n".join([
    "### Your response — Problem 3(a)",
    "",
    "#### Before using AI",
    "",
    "**Aspect I will watch closely** (observation unit, dependence, split, target population, or direction of bias):  ",
    "TODO",
    "",
    "**My one-sentence prediction of what the assistant might get wrong or omit:**  ",
    "TODO",
    "",
    "#### Initial interaction",
    "",
    "**Initial prompt:**  ",
    "TODO",
    "",
    "**Assistant's complete first response:**  ",
    "TODO — paste the complete first response here",
    "",
    "#### Checkable-claim audit",
    "",
    "Use at least two rows. Copy only a short claim excerpt in the first column; do not paste the full response again.",
    "",
    "| Short checkable claim | Course evidence checked | Verdict: supported, revise, or not established | Correction or qualification |",
    "|---|---|---|---|",
    "| TODO | TODO | TODO | TODO |",
    "| TODO | TODO | TODO | TODO |",
])

HW1_P3B_RESPONSE = "\n".join([
    "### Your response — Problem 3(b)",
    "",
    "**Most important weakness or omission:**  ",
    "TODO",
    "",
    "**Why it matters for the new-camera claim (1-2 sentences):**  ",
    "TODO",
])

HW1_P3C_RESPONSE = "\n".join([
    "### Your response — Problem 3(c)",
    "",
    "**Statistical rewrite (2-3 sentences):**  ",
    "TODO — name the frame, dependence, target population, and expected direction of bias",
])

HW1_AI_RECORD = "\n".join([
    "## Required AI-use record (2 points)",
    "",
    "Record only the **initial prompt** for each use. Do not paste follow-up prompts or the full conversation into this table.",
    "",
    "| Assignment part | Tool | Purpose | Initial prompt only | What I checked | What changed after checking | Decision I remained responsible for |",
    "|---|---|---|---|---|---|---|",
    "| Problem 2(e) | TODO | TODO | TODO | TODO | TODO | TODO |",
    "| Problem 3 | TODO | TODO | TODO | TODO | TODO | TODO |",
])

SPECIAL_RESPONSES = {
    ("hw01", "3", "a"): HW1_P3A_RESPONSE,
    ("hw01", "3", "b"): HW1_P3B_RESPONSE,
    ("hw01", "3", "c"): HW1_P3C_RESPONSE,
}

FINAL = "\n".join([
    "## Final submission check",
    "",
    "- [ ] I restarted the runtime and ran all cells from top to bottom.",
    "- [ ] Every requested denominator, table, figure, excerpt, and interpretation is visible.",
    "- [ ] Any handwritten images are legible and each has a typed description or statistical conclusion.",
    "- [ ] Required raw AI prompts/outputs and the AI-use record are preserved.",
    "- [ ] I opened my downloaded PDF and `.ipynb` before uploading them.",
    "",
    "The PDF is the primary grading surface; the notebook is the executable record. Both represent the same work.",
])


def markdown_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(True),
    }


def split_prompt(text: str) -> tuple[str, list[str]]:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
    # Remove print-only page breaks before converting prompts to notebook cells.
    text = re.sub(r"^\\newpage\s*$", "", text, flags=re.M)
    parts = re.split(r"(?=^# Problem \d+)", text, flags=re.M)
    preamble = parts[0].strip()
    problems = [part.strip() for part in parts[1:]]
    if len(problems) != 3:
        raise ValueError(f"Expected three problems; found {len(problems)}")
    return preamble, problems


def problem_cells(problem: str, hw_id: str) -> list[dict]:
    """Split a major problem into small prompt/response cells by lettered subpart."""
    heading_match = re.match(r"^(# Problem \d+[^\n]*)\n+(.*)$", problem, flags=re.S)
    if not heading_match:
        return [markdown_cell(problem), markdown_cell(RESPONSE.format(label="problem"))]
    heading, body = heading_match.groups()
    pieces = re.split(r"(?=^[a-e]\.\s)", body, flags=re.M)
    introduction = pieces[0].strip()
    cells = [markdown_cell(heading + ("\n\n" + introduction if introduction else ""))]
    if len(pieces) == 1:
        cells.append(markdown_cell(RESPONSE.format(label=heading.replace("# ", ""))))
        return cells
    problem_number = re.search(r"Problem (\d+)", heading).group(1)
    for piece in pieces[1:]:
        piece = piece.strip()
        letter = re.match(r"([a-e])\.", piece).group(1)
        cells.append(markdown_cell(piece))
        response = SPECIAL_RESPONSES.get(
            (hw_id, problem_number, letter),
            RESPONSE.format(label=f"Problem {problem_number}({letter})"),
        )
        cells.append(markdown_cell(response))
    return cells


def build_notebook(qmd_path: Path, hw_id: str, label: str) -> dict:
    preamble, problems = split_prompt(qmd_path.read_text())
    cells = [
        markdown_cell(f"# {label} — Colab starter\n\nComplete HW0 before beginning HW1."),
        markdown_cell(WORKFLOW),
        code_cell(build_setup(DATA_GROUPS[hw_id])),
        markdown_cell(preamble),
        code_cell("\n".join(STARTER_LINES[hw_id])),
    ]
    for problem in problems:
        cells.extend(problem_cells(problem, hw_id))
    if hw_id == "hw01":
        cells.append(markdown_cell(HW1_AI_RECORD))
    cells.append(markdown_cell(FINAL))
    for index, cell in enumerate(cells):
        cell["id"] = f"{hw_id}-{index:03d}"
    return {
        "cells": cells,
        "metadata": {
            "colab": {"name": f"{hw_id}_starter.ipynb", "provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    for week, hw_id, label in HOMEWORKS:
        qmd = ROOT / "weeks" / week / f"{hw_id}.qmd"
        output = qmd.with_name(f"{hw_id}_starter.ipynb")
        notebook = build_notebook(qmd, hw_id, label)
        output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {output.relative_to(ROOT)} ({len(notebook['cells'])} cells)")


if __name__ == "__main__":
    main()
