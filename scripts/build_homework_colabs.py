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
    "hw03": ["cfpb", "github_issues"],
    "hw04": ["camera_traps"],
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
        "# HW2: rater summaries, Brier targets, and aligned forecasters",
        "from course_helpers import expand_dynasent_raters, summarize_votes",
        "LABELS = ['negative', 'neutral', 'positive']",
        "def multiclass_brier(prob, outcome):",
        "    prob, outcome = np.asarray(prob), np.asarray(outcome)",
        "    return np.sum((prob - outcome) ** 2)",
        "dynasent_root = DATA_ROOT / 'dynasent'",
        "homework_items = pd.read_csv(dynasent_root / 'homework_items.csv')",
        "forecaster_items = pd.read_csv(dynasent_root / 'forecaster_items.csv')",
        "ratings = expand_dynasent_raters(homework_items)",
        "rater_summary = summarize_votes(ratings, homework_items)",
        "assert ratings.groupby('item_id').size().eq(5).all()",
        "assert np.allclose(rater_summary[[f'p_{label}' for label in LABELS]].sum(axis=1), 1)",
        "# Problem 1 is mathematical work; complete it in the response cells without AI.",
        "# Problem 2 begins with rater_summary. Make denominator-first vote-pattern",
        "# and round tables using the lab workflow, then add the requested figure.",
        "# Problem 3 initially reveals only the IDs and sentences.",
        "# Do not inspect the vote columns until the reveal cell in part (c).",
        "forecaster_items[['item_id', 'sentence']]",
    ],
    "hw03": [
        "# HW3: inspect the design before fitting any model",
        "issues_root = DATA_ROOT / 'github_issues'",
        "github_issues = pd.read_csv(issues_root / 'issues.csv', parse_dates=['created_date'])",
        "assert github_issues['issue_number'].is_unique",
        "assert len(github_issues) == 120",
        "print('Real scikit-learn issue-triage extract:')",
        "display(github_issues.head(3))",
        "display(github_issues['module_label'].value_counts().rename('n').to_frame())",
        "print('Issues by year and module (use this EDA when planning the split):')",
        "display(pd.crosstab(github_issues['created_year'], github_issues['module_label']))",
        "print('Date range:', github_issues['created_date'].min().date(),",
        "      'to', github_issues['created_date'].max().date())",
        "print('Unique reporter groups:', github_issues['reporter_group'].nunique())",
        "print('The balanced extract does not preserve natural module prevalence.')",
        "",
        "# Problem 2 returns to the CFPB data from Lab 3.",
        "cfpb_root = DATA_ROOT / 'cfpb'",
        "complaints = pd.read_csv(cfpb_root / 'complaints.csv')",
        "complaints['date_received'] = pd.to_datetime(complaints['date_received'])",
        "assert complaints['complaint_id'].is_unique",
        "assert len(complaints) == 400",
        "assert complaints.groupby(['received_year', 'product']).size().eq(20).all()",
        "print(f'Loaded {len(complaints)} public-narrative complaints.')",
        "display(complaints[['complaint_id', 'narrative', 'product',",
        "                    'date_received', 'similarity_group', 'n_words']].head(3))",
        "# Problem 2 code appears under the relevant subparts below.",
    ],
    "hw04": [
        "# HW4 setup: vision-model correctness on the homework cameras",
        "# Problem 1 needs no code. Problems 2 and 3 use the objects defined here.",
        "from statsmodels.stats.proportion import proportion_confint",
        "from scipy.stats import norm",
        "camera_root = DATA_ROOT / 'camera_traps'",
        "meta = pd.read_csv(camera_root / 'metadata.csv')",
        "outputs = pd.read_csv(camera_root / 'model_outputs.csv')",
        "splits = pd.read_csv(camera_root / 'splits.csv')",
        "camera = meta.merge(outputs, on='image_id').merge(splits, on='image_id')",
        "camera['correct'] = camera['vision_pred'].eq(camera['animal_present']).astype(int)",
        "hw = camera.query(\"split == 'homework_holdout'\").copy()",
        "print(f\"{len(hw)} frames, {hw['sequence_id'].nunique()} sequences, \"",
        "      f\"{hw['camera_id'].nunique()} cameras\")",
        "assert hw.groupby('sequence_id').size().eq(3).all()",
        "",
        "# Lab 4 function, reused as allowed. It returns all B bootstrap estimates.",
        "def sequence_bootstrap(data, statistic, B=2000, seed=2027):",
        "    \"\"\"Resample whole trigger sequences with replacement; return the B estimates.\"\"\"",
        "    rng = np.random.default_rng(seed)",
        "    ids = np.sort(data['sequence_id'].unique())",
        "    groups = {sid: g for sid, g in data.groupby('sequence_id')}",
        "    estimates = np.empty(B)",
        "    for b in range(B):",
        "        draw = rng.choice(ids, size=len(ids), replace=True)",
        "        sample = pd.concat([groups[s] for s in draw], ignore_index=True)",
        "        estimates[b] = statistic(sample)",
        "    return estimates",
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

HW3_RESPONSE = "\n".join([
    "### Your response - {label}",
    "",
    "Write your answer below in the format requested above. You may instead",
    "insert a clear image of handwritten work; if you do, add a one-sentence",
    "typed summary for accessibility.",
    "",
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

HW2_P2D_RESPONSE = "\n".join([
    "### Your response — Problem 2(d)",
    "",
    "**Chosen alternative before computing:**  ",
    "TODO — choose exactly one of the two listed changes",
    "",
    "| Analysis | Outcome | Retained population | Round 1 estimate | Round 2 estimate | Round 2 minus Round 1 |",
    "|---|---|---|---:|---:|---:|",
    "| Primary | Majority-label accuracy | All 72 assigned items | TODO | TODO | TODO |",
    "| Planned alternative | TODO | TODO | TODO | TODO | TODO |",
    "",
    "**Interpretation (2-3 sentences):**  ",
    "TODO — state what changed and whether the substantive comparison survived",
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

HW2_AI_TABLE = "\n".join([
    "",
    "",
    "| Assignment part | Tool or checkpoint | Purpose | Initial prompt only | What I checked | What changed after checking | Decision I remained responsible for |",
    "|---|---|---|---|---|---|---|",
    "| Problem 2(e) | TODO | TODO | TODO | TODO | TODO | TODO |",
    "| Problem 3 | Cardiff revision `3216a57f`; DistilBERT revision `cf991100` | Generate two frozen probability forecasts | no natural-language prompt | TODO | TODO | TODO |",
])

HW2_P3A_CODE = "\n".join([
    "# Fill one probability per sentence in the displayed row order before running either model.",
    "student_forecasts = forecaster_items[['item_id', 'sentence']].copy()",
    "student_forecasts['student_p_negative'] = [np.nan] * len(student_forecasts)",
    "student_forecasts['student_p_neutral'] = [np.nan] * len(student_forecasts)",
    "student_forecasts['student_p_positive'] = [np.nan] * len(student_forecasts)",
    "# Replace all 30 np.nan entries with your own probabilities, then run this cell.",
    "# Each row must contain three nonnegative numbers that sum to one.",
    "student_forecasts",
])

HW2_P3B_CODE = "\n".join([
    "%pip -q install 'transformers==5.13.0'",
    "from transformers import pipeline",
    "STUDENT_PROB_COLS = [f'student_p_{label}' for label in LABELS]",
    "assert student_forecasts[STUDENT_PROB_COLS].notna().all().all(), (",
    "    'Complete your own forecasts before running the models.'",
    ")",
    "assert np.allclose(student_forecasts[STUDENT_PROB_COLS].sum(axis=1), 1)",
    "student_forecasts['student_label'] = (",
    "    student_forecasts[STUDENT_PROB_COLS].idxmax(axis=1).str.removeprefix('student_p_')",
    ")",
    "MODEL_SPECS = {",
    "    'cardiff': (",
    "        'cardiffnlp/twitter-roberta-base-sentiment-latest',",
    "        '3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7'),",
    "    'distilbert': (",
    "        'lxyuan/distilbert-base-multilingual-cased-sentiments-student',",
    "        'cf991100d706c13c0a080c097134c05b7f436c45'),",
    "}",
    "def run_frozen_forecaster(short_name, sentences):",
    "    model_id, revision = MODEL_SPECS[short_name]",
    "    classifier = pipeline(",
    "        'text-classification', model=model_id, revision=revision,",
    "        top_k=None, device=-1)",
    "    raw = classifier(sentences, truncation=True, batch_size=10)",
    "    rows = []",
    "    for result in raw:",
    "        scores = {entry['label'].lower(): entry['score'] for entry in result}",
    "        rows.append({",
    "            **{f'{short_name}_p_{label}': scores[label] for label in LABELS},",
    "            f'{short_name}_label': max(LABELS, key=scores.get),",
    "        })",
    "    return pd.DataFrame(rows)",
    "model_outputs = forecaster_items[['item_id', 'sentence']].copy()",
    "for short_name in MODEL_SPECS:",
    "    model_outputs = pd.concat([",
    "        model_outputs,",
    "        run_frozen_forecaster(short_name, model_outputs['sentence'].tolist()),",
    "    ], axis=1)",
    "for short_name in MODEL_SPECS:",
    "    cols = [f'{short_name}_p_{label}' for label in LABELS]",
    "    assert np.allclose(model_outputs[cols].sum(axis=1), 1)",
    "model_outputs['models_disagree'] = (",
    "    model_outputs['cardiff_label'] != model_outputs['distilbert_label']",
    ")",
    "model_outputs",
])

HW2_P3C_CODE = "\n".join([
    "# Reveal the five measurements only after locking all three forecasts.",
    "target = forecaster_items.copy()",
    "for label in LABELS:",
    "    target[f'q_{label}'] = target[f'{label}_votes'] / 5",
    "TARGET_COLS = [f'q_{label}' for label in LABELS]",
    "assert target[[f'{label}_votes' for label in LABELS]].sum(axis=1).eq(5).all()",
    "assert np.allclose(target[TARGET_COLS].sum(axis=1), 1)",
    "target['majority_label'] = target[TARGET_COLS].idxmax(axis=1).str.removeprefix('q_')",
    "comparison = (",
    "    student_forecasts.merge(model_outputs, on=['item_id', 'sentence'], validate='one_to_one')",
    "    .merge(target, on=['item_id', 'sentence'], validate='one_to_one')",
    ")",
    "soft_target = comparison[TARGET_COLS].to_numpy()",
    "majority_target = np.column_stack([",
    "    comparison['majority_label'].eq(label).astype(float) for label in LABELS",
    "])",
    "summary_rows = []",
    "for forecaster in ['student', 'cardiff', 'distilbert']:",
    "    prob_cols = [f'{forecaster}_p_{label}' for label in LABELS]",
    "    probabilities = comparison[prob_cols].to_numpy()",
    "    comparison[f'{forecaster}_brier_soft'] = ((probabilities - soft_target) ** 2).sum(axis=1)",
    "    comparison[f'{forecaster}_brier_majority'] = ((probabilities - majority_target) ** 2).sum(axis=1)",
    "    summary_rows.append({",
    "        'forecaster': forecaster,",
    "        'items': len(comparison),",
    "        'mean_brier_vs_rater_proportions': comparison[f'{forecaster}_brier_soft'].mean(),",
    "        'mean_brier_vs_majority_one_hot': comparison[f'{forecaster}_brier_majority'].mean(),",
    "        'majority_matches': (comparison[f'{forecaster}_label'] == comparison['majority_label']).sum(),",
    "    })",
    "forecaster_summary = pd.DataFrame(summary_rows)",
    "display(comparison)",
    "forecaster_summary",
])

HW3_P1B_RESPONSE = "\n".join([
    "### Your response - Problem 1(b)",
    "",
    "| Question | Your answer |",
    "|---|---|",
    "| What module-label classification does the model make, and how would a maintainer use it? | TODO |",
    "| Which scikit-learn GitHub issues should the conclusion cover? | TODO |",
    "| Main performance measure: accuracy or average recall across modules? Why? | TODO |",
    "| Checkpoint 1: What result for the simple title model versus the baseline would count as evidence that titles help? | TODO |",
    "| Checkpoint 2: How much must the transformer improve over logistic regression before you would recommend a pilot? Why? | TODO |",
    "| Quantity 1 in words: simple title model minus no-information rule | TODO |",
    "| Quantity 2 in words: transformer minus simple title model | TODO |",
])

HW3_P1D_RESPONSE = "\n".join([
    "### Your response - Problem 1(d)",
    "",
    "| Part of the plan | Your choice |",
    "|---|---|",
    "| Research question / hypothesis | TODO |",
    "| GitHub issues represented in `github_issues/issues.csv` | TODO |",
    "| Issues you want the conclusion to cover | TODO |",
    "| Rule for keeping `reporter_group` together or allowing it across sets | TODO |",
    "| Two comparisons to estimate | TODO |",
    "| Job of the training data | TODO |",
    "| Job of the validation data | TODO |",
    "| Job of the test data | TODO |",
    "| Main measure and the rule for passing each checkpoint | TODO |",
    "| Decision the study will inform | TODO |",
    "| Intended use and intended user | TODO |",
    "| One out-of-scope use | TODO |",
    "",
    "**If-then decision rule (1-2 sentences):**  ",
    "TODO",
    "",
    "**A favorable result would still not establish (1 sentence):**  ",
    "TODO",
    "",
    "**Model Cards connection:**  ",
    "TODO - cite the relevant subsection of Mitchell et al. Section 4",
])

HW3_P1C_RESPONSE = "\n".join([
    "### Your response - Problem 1(c)",
    "",
    "| Decision | Your answer |",
    "|---|---|",
    "| Complete: Our final comparison is meant to tell us how the two models perform on... | TODO |",
    "| Must GitHub issues from the same `reporter_group` stay together? Why or why not? | TODO |",
    "| Which rows go into training, and what happens there? | TODO |",
    "| Which rows go into validation, and what happens there? | TODO |",
    "| Which rows go into the test set, and what happens there? | TODO |",
    "| Does this split mainly address changes over time, repeated reporters, or both? Explain. | TODO |",
    "| What would a random row split tell us instead? | TODO |",
    "| What would a reporter-held-out split tell us instead? | TODO |",
    "| What can `github_issues/issues.csv` not tell us about other software projects? | TODO |",
])

HW3_P2A_CODE = "\n".join([
    "# Inspect the sample before fitting a model.",
    "product_year_counts = pd.crosstab(",
    "    complaints['received_year'], complaints['product']",
    ")",
    "duplicate_group_sizes = complaints.groupby('similarity_group').size()",
    "duplicate_group_count = int((duplicate_group_sizes > 1).sum())",
    "word_count_percentiles = (",
    "    complaints['n_words'].quantile([0.10, 0.50, 0.90]).rename('n_words')",
    ")",
    "display(product_year_counts)",
    "print('Similarity groups with more than one row:', duplicate_group_count)",
    "display(word_count_percentiles.to_frame())",
    "# TODO: add one assertion that every product-year cell contains 20 rows.",
])

HW3_P2A_RESPONSE = "\n".join([
    "### Your response - Problem 2(a)",
    "",
    "| Check | Result from your output |",
    "|---|---|",
    "| Rows in each product-year cell | TODO |",
    "| Similarity groups with more than one row | TODO |",
    "| 10th / 50th / 90th percentiles of `n_words` | TODO |",
    "",
    "**Interpretation (2-3 sentences):**  ",
    "TODO - explain what the balanced sampling means and why public narratives do not represent all CFPB complaints",
])

HW3_P2B_CODE = "\n".join([
    "# Define the split by calendar year before fitting any model.",
    "SPLIT_BY_YEAR = {2022: 'train', 2023: 'train', 2024: 'validation', 2025: 'test'}",
    "complaints_split = complaints.assign(",
    "    split=complaints['received_year'].map(SPLIT_BY_YEAR)",
    ")",
    "assert complaints_split['split'].notna().all()",
    "split_order = ['train', 'validation', 'test']",
    "split_sizes = complaints_split['split'].value_counts().reindex(split_order)",
    "products_by_split = pd.crosstab(",
    "    complaints_split['split'], complaints_split['product']",
    ").reindex(split_order)",
    "group_split_counts = (",
    "    complaints_split[['similarity_group', 'split']].drop_duplicates()",
    "    .groupby('similarity_group')['split'].nunique()",
    ")",
    "cross_split_groups = group_split_counts[group_split_counts > 1]",
    "display(split_sizes.rename('rows').to_frame())",
    "display(products_by_split)",
    "print('Similarity groups appearing in more than one split:', len(cross_split_groups))",
    "# TODO: add an assertion that the split sizes are 200, 100, and 100.",
    "# TODO: add an assertion that all five products appear in every split.",
    "train = complaints_split.query(\"split == 'train'\").copy()",
    "validation = complaints_split.query(\"split == 'validation'\").copy()",
    "test = complaints_split.query(\"split == 'test'\").copy()",
])

HW3_P2B_RESPONSE = "\n".join([
    "### Your response - Problem 2(b)",
    "",
    "| Check | Result from your output |",
    "|---|---|",
    "| Training / validation / test rows | TODO |",
    "| Products represented in every split | TODO |",
    "| Similarity groups crossing splits | TODO |",
    "",
    "**Why the time split matches the 2025 question (1 sentence):**  ",
    "TODO",
])

HW3_P2C_CODE = "\n".join([
    "from sklearn.feature_extraction.text import TfidfVectorizer",
    "from sklearn.linear_model import LogisticRegression",
    "from sklearn.metrics import accuracy_score",
    "from sklearn.pipeline import make_pipeline",
    "",
    "CANDIDATE_MIN_DF = [1, 2, 5]",
    "",
    "def make_text_model(min_df):",
    "    return make_pipeline(",
    "        TfidfVectorizer(min_df=min_df, ngram_range=(1, 2)),",
    "        LogisticRegression(max_iter=2000, random_state=SEED),",
    "    )",
    "",
    "validation_rows = []",
    "for min_df in CANDIDATE_MIN_DF:",
    "    candidate = make_text_model(min_df)",
    "    candidate.fit(train['narrative'], train['product'])",
    "    validation_prediction = candidate.predict(validation['narrative'])",
    "    validation_rows.append({",
    "        'min_df': min_df,",
    "        'validation_accuracy': accuracy_score(",
    "            validation['product'], validation_prediction",
    "        ),",
    "    })",
    "validation_results = pd.DataFrame(validation_rows)",
    "best_min_df = int(",
    "    validation_results.sort_values(",
    "        ['validation_accuracy', 'min_df'], ascending=[False, True]",
    "    ).iloc[0]['min_df']",
    ")",
    "display(validation_results)",
    "print('Selected min_df:', best_min_df)",
    "# TODO: add an assertion that best_min_df is in CANDIDATE_MIN_DF.",
])

HW3_P2C_RESPONSE = "\n".join([
    "### Your response - Problem 2(c)",
    "",
    "| `min_df` | Validation accuracy |",
    "|---:|---:|",
    "| 1 | TODO |",
    "| 2 | TODO |",
    "| 5 | TODO |",
    "",
    "**Selected value:** TODO  ",
    "",
    "**Why later narratives cannot influence the vocabulary (1-2 sentences):**  ",
    "TODO",
])

HW3_P2D_CODE = "\n".join([
    "from sklearn.dummy import DummyClassifier",
    "",
    "OPEN_TEST = False  # Change to True only after parts (a)-(c) are complete.",
    "",
    "def paired_bootstrap_accuracy_difference(",
    "    y_true, model_prediction, floor_prediction, B=5000, seed=SEED",
    "):",
    "    y_true = np.asarray(y_true)",
    "    model_prediction = np.asarray(model_prediction)",
    "    floor_prediction = np.asarray(floor_prediction)",
    "    paired_gain = (model_prediction == y_true).astype(float) - (",
    "        floor_prediction == y_true",
    "    ).astype(float)",
    "    rng = np.random.default_rng(seed)",
    "    bootstrap_means = np.array([",
    "        rng.choice(paired_gain, size=len(paired_gain), replace=True).mean()",
    "        for _ in range(B)",
    "    ])",
    "    interval = np.quantile(bootstrap_means, [0.025, 0.975])",
    "    return paired_gain.mean(), interval",
    "",
    "if not OPEN_TEST:",
    "    print('Test set remains unopened. Finish parts (a)-(c), then set OPEN_TEST = True.')",
    "else:",
    "    fit_rows = pd.concat([train, validation], ignore_index=True)",
    "    final_model = make_text_model(best_min_df)",
    "    final_model.fit(fit_rows['narrative'], fit_rows['product'])",
    "    no_information = DummyClassifier(strategy='most_frequent')",
    "    no_information.fit(fit_rows[['n_words']], fit_rows['product'])",
    "    model_prediction = final_model.predict(test['narrative'])",
    "    floor_prediction = no_information.predict(test[['n_words']])",
    "    model_accuracy = accuracy_score(test['product'], model_prediction)",
    "    floor_accuracy = accuracy_score(test['product'], floor_prediction)",
    "    improvement, improvement_interval = paired_bootstrap_accuracy_difference(",
    "        test['product'], model_prediction, floor_prediction",
    "    )",
    "    test_results = pd.DataFrame({",
    "        'method': ['No-information classifier', 'TF-IDF logistic regression'],",
    "        'test_accuracy': [floor_accuracy, model_accuracy],",
    "    })",
    "    display(test_results)",
    "    print(f'Paired accuracy improvement: {improvement:.3f}')",
    "    print('Paired bootstrap 95% interval: '",
    "          f'[{improvement_interval[0]:.3f}, {improvement_interval[1]:.3f}]')",
])

HW3_P2D_RESPONSE = "\n".join([
    "### Your response - Problem 2(d)",
    "",
    "| Result | Value |",
    "|---|---:|",
    "| No-information test accuracy | TODO |",
    "| TF-IDF logistic-regression test accuracy | TODO |",
    "| Paired accuracy improvement | TODO |",
    "| Paired bootstrap 95% interval | TODO |",
    "",
    "**Checkpoint 1 conclusion (1-2 sentences):**  ",
    "TODO - say whether the interval clears zero and what that means",
])

HW3_P2E_RESPONSE = "\n".join([
    "### Your response - Problem 2(e)",
    "",
    "| Design decision | Problem in the initial workflow | Supporting code or output |",
    "|---|---|---|",
    "| Time split | TODO | TODO |",
    "| Similarity-group check | TODO | TODO |",
    "| TF-IDF inside the model pipeline | TODO | TODO |",
    "| One-time test evaluation | TODO | TODO |",
    "",
    "**Limitation reduced by the code (1 sentence):**  ",
    "TODO",
    "",
    "**Limitation the code cannot solve (1 sentence):**  ",
    "TODO - discuss selection into the public-narrative dataset",
])

HW3_P2F_CODE = "\n".join([
    "# Stretch workspace: paste or adapt the AI-assisted simulation below.",
    "# Keep a fixed seed and show the group overlap and accuracy for both splits.",
    "STRETCH_SEED = SEED",
    "# TODO: add and run your final simulation code in this cell or new cells below.",
])

HW3_P2F_RESPONSE = "\n".join([
    "### Your response - Problem 2(f)",
    "",
    "**Prediction recorded before using AI:**  ",
    "TODO",
    "",
    "| Split | Groups shared by training and test | Accuracy |",
    "|---|---:|---:|",
    "| Random row split | TODO | TODO |",
    "| Group-held-out split | TODO | TODO |",
    "",
    "**What happened and why (2-3 sentences):**  ",
    "TODO",
    "",
    "**Connection to complaint `similarity_group` (1-2 sentences):**  ",
    "TODO",
    "",
    "**One way the simulation is less realistic (1 sentence):**  ",
    "TODO",
])

HW3_P3A_RESPONSE = "\n".join([
    "### Your response - Problem 3(a)",
    "",
    "| What to compare | Original-request answer: evidence or omission | Detailed-request answer: evidence or omission | What you conclude |",
    "|---|---|---|---|",
    "| Target population and outcome | TODO | TODO | TODO |",
    "| Unit and split | TODO | TODO | TODO |",
    "| No-information rule, simple model, and transformer comparison | TODO | TODO | TODO |",
    "| Uncertainty and practical importance | TODO | TODO | TODO |",
    "| Supported claim and decision | TODO | TODO | TODO |",
])

HW3_AI_TABLE = "\n".join([
    "",
    "",
    "| Assignment part | Tool | Purpose | Initial prompt only | What I checked | What changed after checking | Decision I remained responsible for |",
    "|---|---|---|---|---|---|---|",
    "| Problem 2(f) | TODO | Build the exploratory grouped-split simulation | TODO | TODO | TODO | TODO |",
    "| Problem 3 original request | TODO | Obtain an analysis plan from the original request | TODO | TODO | TODO | TODO |",
    "| Problem 3 detailed request | TODO | Obtain a plan based on the completed design brief | TODO | TODO | TODO | TODO |",
])

HW3_AI_APPENDIX = "\n".join([
    "## Appendix A: Raw AI evidence",
    "",
    "Paste the two complete **first** plan outputs below. Preserve the wording",
    "exactly as returned. Do not include follow-up conversation turns.",
    "",
    "### A1. Weak-request plan output",
    "",
    "TODO - paste the complete first response here",
    "",
    "### A2. Specified-request plan output",
    "",
    "TODO - paste the complete first response here",
    "",
    "**Appendix check:** Both entries contain the complete first response and no",
    "follow-up turns. The same tool/model and data context were used for both.",
])

HW4_P1_HEADER = "\n".join([
    "### Your response - Problem 1({letter})",
    "",
    "Show your work. Type it in Markdown/LaTeX, or insert a clear image of handwritten work",
    "followed by one typed sentence stating your conclusion.",
    "",
])

def _hw4_p1_response(letter, parts):
    lines = [HW4_P1_HEADER.format(letter=letter)]
    for part in parts:
        lines += [f"**{part}**  ", "TODO", ""]
    return "\n".join(lines).rstrip() + "\n"

HW4_P1A_RESPONSE = _hw4_p1_response("a", ["(i)", "(ii)", "(iii)", "(iv) 1.", "(iv) 2.", "(iv) 3."])
HW4_P1B_RESPONSE = _hw4_p1_response("b", ["(i)", "(ii)", "(iii)", "(iv)", "(v)"])
HW4_P1C_RESPONSE = _hw4_p1_response("c", [
    "(i) 1.", "(i) 2.", "(i) 3.", "(ii) 1.", "(ii) 2.",
    "(iii) 1.", "(iii) 2.", "(iii) 3.", "(iv)", "(v)",
])

HW4_P2A_CODE = "\n".join([
    "# Problem 2(a): code the Wilson center and plus-minus term from Problem 1(a)(ii)",
    "z = norm.ppf(0.975)",
    "k = int(hw['correct'].sum())",
    "n = len(hw)",
    "p_hat = k / n",
    "",
    "def wilson_interval(k, n, z):",
    "    p_hat = k / n",
    "    p_tilde = np.nan  # TODO: your formula for the center",
    "    h = np.nan        # TODO: your formula for the plus-minus term",
    "    return p_tilde - h, p_tilde + h",
    "",
    "wald_pm = np.nan  # TODO: the Wald plus-minus term",
    "comparison = pd.DataFrame({",
    "    'interval': ['Wald', 'Wilson (my formula)', 'Wilson (statsmodels)'],",
    "    'lower': [p_hat - wald_pm, wilson_interval(k, n, z)[0], proportion_confint(k, n, method='wilson')[0]],",
    "    'upper': [p_hat + wald_pm, wilson_interval(k, n, z)[1], proportion_confint(k, n, method='wilson')[1]],",
    "})",
    "print(f'{k} correct out of {n} frames, accuracy {p_hat:.3f}')",
    "comparison.round(3)",
])

HW4_P2B_CODE = "\n".join([
    "# Problem 2(b): sequence bootstrap with the Lab 4 function (about 10 seconds)",
    "estimates = sequence_bootstrap(hw, lambda d: d['correct'].mean(), B=2000, seed=2027)",
    "print('sequences resampled in each draw:', hw['sequence_id'].nunique())",
    "boot_interval = np.quantile(estimates, [0.025, 0.975])",
    "boot_var = estimates.var(ddof=1)",
    "print('95% percentile interval:', boot_interval.round(3))",
    "print('bootstrap variance:', round(boot_var, 5))",
    "",
    "design_effect = np.nan   # TODO: step 1",
    "effective_n = np.nan     # TODO: step 1",
    "rho_hat = np.nan         # TODO: step 2, solve your Problem 1(c) formula for rho",
    "print('design effect:', design_effect, ' effective n:', effective_n, ' rho:', rho_hat)",
])

HW4_P3A_CODE = "\n".join([
    "# Problem 3(a): the AI's attempted 'sequence bootstrap' and the supplied checks",
    "def ai_bootstrap_attempt(dat, seed=401):",
    "    \"\"\"Return identifiers selected for one alleged 'sequence bootstrap'.\"\"\"",
    "    sampled_frames = dat.sample(n=len(dat), replace=True, random_state=seed)",
    "    return sampled_frames['sequence_id'].tolist()",
    "",
    "def expand_sequence_draws(dat, sequence_draws):",
    "    \"\"\"Expand sampled sequence IDs into complete blocks of their frames.\"\"\"",
    "    blocks = []",
    "    for draw_id, sequence_id in enumerate(sequence_draws):",
    "        block = dat.loc[dat['sequence_id'].eq(sequence_id)].copy()",
    "        block['bootstrap_draw_id'] = draw_id",
    "        blocks.append(block)",
    "    return pd.concat(blocks, ignore_index=True)",
    "",
    "def supplied_checks(candidate, dat):",
    "    \"\"\"A correct candidate returns one sequence ID per original sequence.\"\"\"",
    "    draws = candidate(dat, seed=401)",
    "    n_sequences = dat['sequence_id'].nunique()",
    "    assert len(draws) == n_sequences, 'Draw complete sequences, not frames.'",
    "    assert set(draws).issubset(set(dat['sequence_id'])), 'Return sequence IDs.'",
    "    duplicated = pd.concat([dat, dat.iloc[[0]]], ignore_index=True)",
    "    assert len(candidate(duplicated, seed=401)) == n_sequences, (",
    "        'Duplicating a frame must not increase the number of sequence draws.')",
    "    expanded = expand_sequence_draws(dat, draws)",
    "    for _, block in expanded.groupby('bootstrap_draw_id'):",
    "        assert block['sequence_id'].nunique() == 1",
    "        source_n = dat['sequence_id'].eq(block['sequence_id'].iloc[0]).sum()",
    "        assert len(block) == source_n, 'Every draw must contain a complete sequence.'",
    "",
    "try:",
    "    supplied_checks(ai_bootstrap_attempt, hw)",
    "    print('original: passed')",
    "except AssertionError as error:",
    "    print('original: failed -', error)",
    "",
    "# TODO: paste the corrected function here, name it corrected_bootstrap, and run:",
    "# supplied_checks(corrected_bootstrap, hw); print('corrected: passed')",
])

HW4_P3A_RESPONSE = "\n".join([
    "### Your response - Problem 3(a)",
    "",
    "**My prompt (no mention of the bug):**  ",
    "TODO",
    "",
    "**The assistant's complete first response:**  ",
    "TODO",
    "",
    "**Did it notice the wrong resampling unit? Quote the relevant part or say it missed it:**  ",
    "TODO",
    "",
    "**What I changed if the AI's fix failed the checks:**  ",
    "TODO or not applicable",
])

HW4_AI_RECORD = "\n".join([
    "## Required AI-use record (2 points)",
    "",
    "Record only the **initial prompt** for each use. Do not paste follow-up prompts or the full conversation into this table.",
    "",
    "| Assignment part | Tool | Purpose | Initial prompt only | What I checked | What changed after checking | Decision I made myself |",
    "|---|---|---|---|---|---|---|",
    "| Problem 2 (if AI was used) | TODO | TODO | TODO | TODO | TODO | TODO |",
    "| Problem 3 | TODO | TODO | TODO | TODO | TODO | TODO |",
])

SPECIAL_RESPONSES = {
    ("hw01", "3", "a"): HW1_P3A_RESPONSE,
    ("hw01", "3", "b"): HW1_P3B_RESPONSE,
    ("hw01", "3", "c"): HW1_P3C_RESPONSE,
    ("hw02", "2", "d"): HW2_P2D_RESPONSE,
    ("hw03", "1", "b"): HW3_P1B_RESPONSE,
    ("hw03", "1", "c"): HW3_P1C_RESPONSE,
    ("hw03", "1", "d"): HW3_P1D_RESPONSE,
    ("hw03", "2", "a"): HW3_P2A_RESPONSE,
    ("hw03", "2", "b"): HW3_P2B_RESPONSE,
    ("hw03", "2", "c"): HW3_P2C_RESPONSE,
    ("hw03", "2", "d"): HW3_P2D_RESPONSE,
    ("hw03", "2", "e"): HW3_P2E_RESPONSE,
    ("hw03", "2", "f"): HW3_P2F_RESPONSE,
    ("hw03", "3", "a"): HW3_P3A_RESPONSE,
    ("hw04", "1", "a"): HW4_P1A_RESPONSE,
    ("hw04", "1", "b"): HW4_P1B_RESPONSE,
    ("hw04", "1", "c"): HW4_P1C_RESPONSE,
    ("hw04", "3", "a"): HW4_P3A_RESPONSE,
}

SPECIAL_CODE_BEFORE_RESPONSE = {
    ("hw02", "3", "a"): HW2_P3A_CODE,
    ("hw02", "3", "b"): HW2_P3B_CODE,
    ("hw02", "3", "c"): HW2_P3C_CODE,
    ("hw03", "2", "a"): HW3_P2A_CODE,
    ("hw03", "2", "b"): HW3_P2B_CODE,
    ("hw03", "2", "c"): HW3_P2C_CODE,
    ("hw03", "2", "d"): HW3_P2D_CODE,
    ("hw03", "2", "f"): HW3_P2F_CODE,
    ("hw04", "2", "a"): HW4_P2A_CODE,
    ("hw04", "2", "b"): HW4_P2B_CODE,
    ("hw04", "3", "a"): HW4_P3A_CODE,
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
    subpart_pattern = r"(?=^[a-f]\.\s)" if hw_id == "hw03" else r"(?=^[a-e]\.\s)"
    pieces = re.split(subpart_pattern, body, flags=re.M)
    introduction = pieces[0].strip()
    cells = [markdown_cell(heading + ("\n\n" + introduction if introduction else ""))]
    if len(pieces) == 1:
        cells.append(markdown_cell(RESPONSE.format(label=heading.replace("# ", ""))))
        return cells
    problem_number = re.search(r"Problem (\d+)", heading).group(1)
    for piece in pieces[1:]:
        piece = piece.strip()
        letter = re.match(r"([a-f])\.", piece).group(1)
        cells.append(markdown_cell(piece))
        special_code = SPECIAL_CODE_BEFORE_RESPONSE.get(
            (hw_id, problem_number, letter)
        )
        if special_code:
            cells.append(code_cell(special_code))
        default_response = HW3_RESPONSE if hw_id == "hw03" else RESPONSE
        response = SPECIAL_RESPONSES.get(
            (hw_id, problem_number, letter),
            default_response.format(label=f"Problem {problem_number}({letter})"),
        )
        cells.append(markdown_cell(response))
    return cells


def build_notebook(qmd_path: Path, hw_id: str, label: str) -> dict:
    preamble, problems = split_prompt(qmd_path.read_text())
    cells = [
        markdown_cell(f"# {label} — Colab starter\n\nComplete the assigned preparation before beginning."),
        markdown_cell(WORKFLOW),
        code_cell(build_setup(DATA_GROUPS[hw_id])),
        markdown_cell(preamble),
        code_cell("\n".join(STARTER_LINES[hw_id])),
    ]
    for problem in problems:
        cells.extend(problem_cells(problem, hw_id))
    if hw_id == "hw01":
        cells.append(markdown_cell(HW1_AI_RECORD))
    if hw_id == "hw02":
        for cell in cells:
            if cell["cell_type"] == "markdown" and "## Required AI-use record" in "".join(cell["source"]):
                cell["source"] = ("".join(cell["source"]) + HW2_AI_TABLE).splitlines(True)
                break
    if hw_id == "hw03":
        for cell in cells:
            if cell["cell_type"] == "markdown" and "## Required AI-use record" in "".join(cell["source"]):
                cell["source"] = ("".join(cell["source"]) + HW3_AI_TABLE).splitlines(True)
                break
        cells.append(markdown_cell(HW3_AI_APPENDIX))
    if hw_id == "hw04":
        for cell in cells:
            text = "".join(cell["source"])
            if cell["cell_type"] == "markdown" and "## Required AI-use record" in text:
                cell["source"] = text.split("## Required AI-use record")[0].rstrip().splitlines(True)
                break
        cells.append(markdown_cell(HW4_AI_RECORD))
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
