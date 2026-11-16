"""Build seven student-facing Colab homework notebooks from the QMD prompts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from colab_data_setup import build_common_imports, build_simple_setup


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
    "hw05": ["llm_bbh"],
    "hw06": ["camelyon17"],
    "hw07": ["llm_judges"],
}

STARTER_LINES = {
    "hw01": [
        "# HW1: baseline fit and paired cases (Problem 1 is mathematical work)",
        "def sigmoid(z):",
        "    return 1 / (1 + np.exp(-z))",
        "# Problem 1: show your derivations in the response cells; no AI assistance.",
        "camera_root = data_dir / 'camera_traps'",
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
        "dynasent_root = data_dir / 'dynasent'",
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
        "issues_root = data_dir / 'github_issues'",
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
        "cfpb_root = data_dir / 'cfpb'",
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
        "# Additional library for this homework",
        "from statsmodels.stats.proportion import proportion_confint",
        "",
        "# Read the three Camera Traps tables.",
        "camera_dir = data_dir / \"camera_traps\"",
        "metadata = pd.read_csv(camera_dir / \"metadata.csv\")",
        "model_outputs = pd.read_csv(camera_dir / \"model_outputs.csv\")",
        "splits = pd.read_csv(camera_dir / \"splits.csv\")",
        "",
        "# Join them into one table with one row per frame.",
        "frames = pd.merge(metadata, model_outputs, on=\"image_id\")",
        "frames = pd.merge(frames, splits, on=\"image_id\")",
        "",
        "# correct = 1 if the vision model got the frame right, 0 if not.",
        "frames[\"correct\"] = (frames[\"vision_pred\"] == frames[\"animal_present\"]).astype(int)",
        "",
        "# Keep only the homework cameras. Problem 1 needs no code.",
        "homework = frames[frames[\"split\"] == \"homework_holdout\"]",
        "",
        "print(\"Frames:   \", len(homework))",
        "print(\"Sequences:\", homework[\"sequence_id\"].nunique())",
        "print(\"Cameras:  \", homework[\"camera_id\"].nunique())",
    ],
    "hw05": [
        "# Additional library for this homework",
        "from scipy.stats import binomtest",
        "",
        "# Read the three BBH tables.",
        "bbh_dir = data_dir / \"llm_bbh\"",
        "correct = pd.read_csv(bbh_dir / \"correct.csv\")      # one row per question; 1 = right, 0 = wrong",
        "questions = pd.read_csv(bbh_dir / \"questions.csv\")  # question text, answer, number of options",
        "models = pd.read_csv(bbh_dir / \"models.csv\")        # one row per model",
        "",
        "print(\"Questions:\", len(correct))",
        "print(\"Tasks:    \", correct[\"task\"].nunique())",
        "display(models[[\"column\", \"model\", \"parameters_billion\", \"memory_gb_16bit\"]])",
        "",
        "# Look at one question from each of two tasks. Try other question_id values.",
        "for question_id in [\"hyperbaton_000\", \"tracking_shuffled_objects_three_objects_000\"]:",
        "    question = questions[questions[\"question_id\"] == question_id]",
        "    print(\"\\n---\", question_id, \"---\")",
        "    print(question[\"input\"].iloc[0])",
        "    print(\"Right answer:\", question[\"target\"].iloc[0])",
    ],
    "hw06": [
        "# Additional library for this homework",
        "from statsmodels.stats.proportion import proportion_confint",
        "",
        "# Read the patch table and the images, as in Lab 9. Row i of the table matches image i.",
        "c17_dir = data_dir / \"camelyon17\"",
        "patches = pd.read_csv(c17_dir / \"patches.csv\")",
        "images = np.load(c17_dir / \"patches.npz\")[\"images\"]",
        "",
        "# correct = 1 if the model's call matches the pathologist's label, 0 if not.",
        "patches[\"correct\"] = (patches[\"predicted_tumor\"] == patches[\"label\"]).astype(int)",
        "",
        "# Two measurements that need no label, each averaged over a patch's pixels:",
        "# blue minus red (larger is bluer, as in Lab 9) and brightness (smaller is darker).",
        "blue_minus_red = []",
        "brightness = []",
        "for i in range(len(images)):",
        "    pixels = images[i].astype(float)",
        "    blue_minus_red.append(np.mean(pixels[:, :, 2] - pixels[:, :, 0]))",
        "    brightness.append(np.mean(pixels))",
        "patches[\"blue_minus_red\"] = blue_minus_red",
        "patches[\"brightness\"] = brightness",
        "",
        "benchmark = patches[patches[\"group\"] == \"benchmark\"]",
        "hospital_4 = patches[patches[\"group\"] == \"hospital 4\"]",
        "print(\"Benchmark: \", len(benchmark), \"patches from\", benchmark[\"slide_id\"].nunique(), \"slides at hospitals 1-3\")",
        "print(\"Hospital 4:\", len(hospital_4), \"patches from\", hospital_4[\"slide_id\"].nunique(), \"slides\")",
        "# Do not look at hospital 4's accuracy until Problem 2(d).",
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
    "### Your response - {label}",
    "",
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
    "#### Claim-by-claim check",
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
    "Show your work. Type it in Markdown/LaTeX, or insert a clear photo of handwritten work.",
    "If you insert a photo, add one typed sentence with your answer.",
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
    "# Problem 2(a): two intervals for the vision model's accuracy",
    "k = homework[\"correct\"].sum()     # number of correct frames",
    "n = len(homework)                 # number of frames",
    "p_hat = k / n",
    "print(\"Correct frames:\", k, \"of\", n, \"  accuracy:\", round(p_hat, 3))",
    "",
    "wilson_lower, wilson_upper = proportion_confint(k, n, method=\"wilson\")",
    "print(\"Wilson:         \", round(wilson_lower, 3), \"to\", round(wilson_upper, 3))",
    "",
    "# TODO: compute and print the Clopper-Pearson interval (method=\"beta\").",
])

HW4_P2B_CODE = "\n".join([
    "# Problem 2(b): the Lab 4 sequence bootstrap. You may reuse it as is.",
    "def sequence_bootstrap(data, B=2000, seed=2027):",
    "    \"\"\"Resample whole trigger sequences and return B bootstrap accuracies.\"\"\"",
    "    rng = np.random.default_rng(seed)",
    "",
    "    # The distinct sequence IDs, sorted so the results are reproducible.",
    "    sequence_ids = np.sort(data[\"sequence_id\"].unique())",
    "    n_sequences = len(sequence_ids)",
    "",
    "    accuracies = np.zeros(B)",
    "    for b in range(B):",
    "        # Draw n_sequences sequence IDs with replacement.",
    "        drawn_ids = rng.choice(sequence_ids, size=n_sequences, replace=True)",
    "",
    "        # Collect all the frames from each drawn sequence.",
    "        pieces = []",
    "        for sequence_id in drawn_ids:",
    "            sequence_frames = data[data[\"sequence_id\"] == sequence_id]",
    "            pieces.append(sequence_frames)",
    "        bootstrap_sample = pd.concat(pieces)",
    "",
    "        # Accuracy in this bootstrap sample.",
    "        accuracies[b] = bootstrap_sample[\"correct\"].mean()",
    "",
    "    return accuracies",
    "",
    "",
    "accuracies = sequence_bootstrap(homework, B=2000, seed=2027)   # takes about 15 seconds",
    "lower, upper = np.quantile(accuracies, [0.025, 0.975])",
    "bootstrap_variance = np.var(accuracies, ddof=1)",
    "",
    "print(\"Sequences resampled in each draw:\", homework[\"sequence_id\"].nunique())",
    "print(\"95% percentile interval:\", round(lower, 3), round(upper, 3))",
    "print(\"Bootstrap variance:\", round(bootstrap_variance, 5))",
    "",
    "# TODO step 1: the design effect and the effective sample size",
    "design_effect = np.nan",
    "effective_n = np.nan",
    "",
    "# TODO step 2: solve your Problem 1(c) formula for rho",
    "rho_hat = np.nan",
    "",
    "print(\"Design effect:\", design_effect)",
    "print(\"Effective sample size:\", effective_n)",
    "print(\"Estimated rho:\", rho_hat)",
])

HW4_P3A_CODE = "\n".join([
    "# Problem 3(a): the AI's attempted sequence bootstrap",
    "def ai_bootstrap_attempt(data, seed=401):",
    "    \"\"\"Supposed to return the sequence IDs chosen in one sequence-bootstrap draw.\"\"\"",
    "    sampled_frames = data.sample(n=len(data), replace=True, random_state=seed)",
    "    return list(sampled_frames[\"sequence_id\"])",
    "",
    "",
    "def supplied_checks(candidate, data):",
    "    \"\"\"Tests that any correct one-draw sequence bootstrap should pass.\"\"\"",
    "    n_sequences = data[\"sequence_id\"].nunique()",
    "    valid_ids = list(data[\"sequence_id\"].unique())",
    "",
    "    # Check 1: the number of draws.",
    "    draws = candidate(data, seed=401)",
    "    assert len(draws) == n_sequences, f\"Expected {n_sequences} draws, got {len(draws)}.\"",
    "",
    "    # Check 2: what each draw is.",
    "    for sequence_id in draws:",
    "        assert sequence_id in valid_ids, \"Return sequence IDs.\"",
    "",
    "    # Check 3: add a copy of one row and draw again.",
    "    data_plus_copy = pd.concat([data, data.head(1)])",
    "    draws_again = candidate(data_plus_copy, seed=401)",
    "    assert len(draws_again) == n_sequences, f\"After adding one row: expected {n_sequences} draws, got {len(draws_again)}.\"",
    "",
    "",
    "# Run the checks on the original function.",
    "# The try/except lets the notebook keep running when a check fails.",
    "try:",
    "    supplied_checks(ai_bootstrap_attempt, homework)",
    "    print(\"Original function: passed\")",
    "except AssertionError as error:",
    "    print(\"Original function: failed -\", error)",
    "",
    "# TODO: paste the corrected function below and name it corrected_bootstrap.",
    "# Then remove the # from the next two lines and run this cell again.",
    "# supplied_checks(corrected_bootstrap, homework)",
    "# print(\"Corrected function: passed\")",
])

HW4_P2A_RESPONSE = "\n".join([
    "### Your response - Problem 2(a)",
    "",
    "**Which interval you would report to the team, and why (2 sentences):**  ",
    "TODO",
])

HW4_P2B_RESPONSE = "\n".join([
    "### Your response - Problem 2(b)",
    "",
    "**Sequence bootstrap interval, and what one draw resamples:**  ",
    "TODO",
    "",
    "**1. Design effect and effective sample size:**  ",
    "TODO",
    "",
    "**2. Estimated rho (show the formula you solved):**  ",
    "TODO",
    "",
    "**3. Why the bootstrap interval is wider (2 sentences):**  ",
    "TODO",
])

HW4_P2C_RESPONSE = "\n".join([
    "### Your response - Problem 2(c)",
    "",
    "**1. Result sentence:**  ",
    "TODO",
    "",
    "**2. Why neither interval covers differences between cameras, and the data you would need (2-3 sentences):**  ",
    "TODO",
])

HW4_P3B_RESPONSE = "\n".join([
    "### Your response - Problem 3(b)",
    "",
    "**How the original function's interval width compares with a correct one (show your calculation):**  ",
    "TODO",
    "",
    "**Why code that runs without errors can still report the wrong standard error (1-2 sentences):**  ",
    "TODO",
])

HW4_P3A_RESPONSE = "\n".join([
    "### Your response - Problem 3(a)",
    "",
    "**My prompt:**  ",
    "TODO",
    "",
    "**The assistant's complete first response:**  ",
    "TODO",
    "",
    "**What the checks showed, and what is wrong in my own words:**  ",
    "TODO",
    "",
    "**Did the AI find it? Quote the relevant part or say it missed it:**  ",
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


HW5_P1_RESPONSES = {
    "a": _hw4_p1_response("a", ["(i)", "(ii)", "(iii) 1.", "(iii) 2.", "(iii) 3.", "(iv)"]),
    "b": _hw4_p1_response("b", ["(i)", "(ii)", "(iii)"]),
    "c": _hw4_p1_response("c", ["(i)", "(ii) 1.", "(ii) 2.", "(iii)", "(iv)", "(v)"]),
    "d": _hw4_p1_response("d", ["(i)", "(ii)"]),
}

HW5_P2A_CODE = "\n".join([
    "# Problem 2(a): reference points",
    "print(\"Questions:\", len(correct))",
    "print(\"Tasks:    \", correct[\"task\"].nunique())",
    "",
    "# Guessing at random gets a question right with probability 1 / (number of options).",
    "guess_accuracy = (1 / questions[\"n_options\"]).mean()",
    "print(\"Random guessing:\", round(guess_accuracy, 3))",
    "",
    "# The accuracy of every model, largest model first.",
    "for column in models[\"column\"]:",
    "    print(column, round(correct[column].mean(), 3))",
])

HW5_P2B_CODE = "\n".join([
    "# Problem 2(b): the paired table",
    "qwen = correct[\"qwen25_7b\"]   # model A, the team's current model",
    "phi = correct[\"phi35_mini\"]   # model B, the smaller candidate",
    "n = len(correct)",
    "",
    "n11 = ((qwen == 1) & (phi == 1)).sum()   # both right",
    "n10 = ((qwen == 1) & (phi == 0)).sum()   # only Qwen right",
    "n01 = ((qwen == 0) & (phi == 1)).sum()   # only Phi right",
    "n00 = ((qwen == 0) & (phi == 0)).sum()   # both wrong",
    "",
    "table = pd.DataFrame({\"Phi right\": [n11, n01], \"Phi wrong\": [n10, n00]},",
    "                     index=[\"Qwen right\", \"Qwen wrong\"])",
    "display(table)",
    "",
    "delta_hat = (n01 - n10) / n",
    "print(\"Difference, Phi minus Qwen:\", round(delta_hat, 4))",
    "",
    "# Exact McNemar test: if the models are equally accurate,",
    "# n01 is Binomial(n10 + n01, 1/2), as in Problem 1(a).",
    "mcnemar = binomtest(int(n01), int(n10 + n01), 0.5)",
    "print(\"McNemar exact p-value:\", round(mcnemar.pvalue, 4))",
    "",
    "# TODO: the paired standard error, s_D / sqrt(n), with D = phi - qwen",
    "se_paired = np.nan",
    "",
    "# TODO: the standard error if the two accuracies came from different questions",
    "se_unpaired = np.nan",
    "",
    "print(\"Paired SE:  \", se_paired)",
    "print(\"Unpaired SE:\", se_unpaired)",
    "print(\"Ratio:      \", se_unpaired / se_paired)",
])

HW5_P2C_CODE = "\n".join([
    "# Problem 2(c), step 1: the difference in each task",
    "by_task = correct.groupby(\"task\")[[\"qwen25_7b\", \"phi35_mini\"]].mean()",
    "by_task[\"difference\"] = by_task[\"phi35_mini\"] - by_task[\"qwen25_7b\"]",
    "by_task = by_task.sort_values(\"difference\")",
    "",
    "fig, ax = plt.subplots(figsize=(7, 7))",
    "ax.scatter(100 * by_task[\"difference\"], by_task.index)",
    "ax.axvline(0, color=\"gray\", linestyle=\"--\")",
    "ax.axvline(100 * delta_hat, color=\"tab:red\", label=\"all 5,761 questions\")",
    "ax.set_xlabel(\"Phi minus Qwen, percentage points\")",
    "ax.set_title(\"Difference in accuracy, by BBH task\")",
    "ax.legend()",
    "plt.tight_layout()",
    "plt.show()",
    "",
    "",
    "# Problem 2(c), step 2: the paired task bootstrap",
    "# The Lab 5 task bootstrap. You may reuse it as is.",
    "def task_bootstrap(data, model_a, model_b, B=2000, seed=2027):",
    "    \"\"\"Resample whole tasks and return B bootstrap differences, model_b minus model_a.\"\"\"",
    "    rng = np.random.default_rng(seed)",
    "",
    "    # The distinct task names, sorted so the results are reproducible.",
    "    task_names = np.sort(data[\"task\"].unique())",
    "    n_tasks = len(task_names)",
    "",
    "    differences = np.zeros(B)",
    "    for b in range(B):",
    "        # Draw n_tasks task names with replacement.",
    "        drawn_tasks = rng.choice(task_names, size=n_tasks, replace=True)",
    "",
    "        # Collect every question from each drawn task. Each row keeps",
    "        # both models' results, so the pairs stay together.",
    "        pieces = []",
    "        for task in drawn_tasks:",
    "            task_rows = data[data[\"task\"] == task]",
    "            pieces.append(task_rows)",
    "        bootstrap_sample = pd.concat(pieces)",
    "",
    "        # The difference in accuracy in this bootstrap sample.",
    "        differences[b] = bootstrap_sample[model_b].mean() - bootstrap_sample[model_a].mean()",
    "",
    "    return differences",
    "",
    "",
    "differences = task_bootstrap(correct, \"qwen25_7b\", \"phi35_mini\")   # Phi minus Qwen; takes about 10 seconds",
    "lower, upper = np.quantile(differences, [0.025, 0.975])",
    "se_task = np.std(differences, ddof=1)",
    "",
    "print(\"Tasks resampled in each draw:\", correct[\"task\"].nunique())",
    "print(\"95% percentile interval:\", round(lower, 4), round(upper, 4))",
    "print(\"Task bootstrap SE:\", round(se_task, 5))",
    "",
    "# TODO: how many times larger is se_task than se_paired from 2(b)?",
])

HW5_P2D_CODE = "\n".join([
    "# Problem 2(d): non-inferiority",
    "margin = 0.03   # set by the team before seeing the data",
    "",
    "# The 5th percentile of the bootstrap differences is a one-sided 95% lower bound.",
    "lower_bound_task = np.quantile(differences, 0.05)",
    "print(\"One-sided lower bound, task bootstrap:\", round(lower_bound_task, 4))",
    "print(\"Margin:\", -margin)",
    "",
    "# TODO for part 3: the lower bound from the paired SE, delta_hat - 1.645 * se_paired,",
    "# and both conclusions at a 1-point margin.",
    "",
    "# For part 4: each model's size and memory for its weights at 16-bit precision.",
    "display(models[[\"column\", \"parameters_billion\", \"memory_gb_16bit\", \"license\"]])",
])

HW5_P2E_CODE = "\n".join([
    "# Problem 2(e): picking the tasks to report",
    "def phi_advantage(data):",
    "    \"\"\"Phi's accuracy minus Qwen's accuracy.\"\"\"",
    "    return data[\"phi35_mini\"].mean() - data[\"qwen25_7b\"].mean()",
    "",
    "",
    "def pick_tasks(data, n_picked=5, B=500, seed=2027):",
    "    \"\"\"Split each task in half at random, pick the n_picked tasks where Phi looks best",
    "    on the first half, and score those tasks on both halves. Repeat B times.\"\"\"",
    "    rng = np.random.default_rng(seed)",
    "    task_names = np.sort(data[\"task\"].unique())",
    "",
    "    first_half_advantage = np.zeros(B)",
    "    second_half_advantage = np.zeros(B)",
    "    for b in range(B):",
    "        # Put each question in half 1 or half 2, splitting every task evenly.",
    "        half = pd.Series(0, index=data.index)",
    "        for task in task_names:",
    "            task_rows = data.index[data[\"task\"] == task]",
    "            shuffled = rng.permutation(task_rows)",
    "            n_first = len(task_rows) // 2",
    "            half.loc[shuffled[:n_first]] = 1",
    "            half.loc[shuffled[n_first:]] = 2",
    "        first = data[half == 1]",
    "        second = data[half == 2]",
    "",
    "        # Phi's advantage in each task, using the first half only.",
    "        phi_by_task = first.groupby(\"task\")[\"phi35_mini\"].mean()",
    "        qwen_by_task = first.groupby(\"task\")[\"qwen25_7b\"].mean()",
    "        gaps = phi_by_task - qwen_by_task",
    "",
    "        # The n_picked tasks where Phi looks best.",
    "        picked = gaps.sort_values(ascending=False).index[:n_picked]",
    "",
    "        # Score the picked tasks on each half.",
    "        first_half_advantage[b] = phi_advantage(first[first[\"task\"].isin(picked)])",
    "        second_half_advantage[b] = phi_advantage(second[second[\"task\"].isin(picked)])",
    "",
    "    return first_half_advantage, second_half_advantage",
    "",
    "",
    "first_half_advantage, second_half_advantage = pick_tasks(correct)   # takes a few seconds",
    "print(\"Picked tasks, first half: \", round(first_half_advantage.mean(), 4))",
    "print(\"Picked tasks, second half:\", round(second_half_advantage.mean(), 4))",
    "print(\"All questions:            \", round(phi_advantage(correct), 4))",
])

HW5_P2A_RESPONSE = "\n".join([
    "### Your response - Problem 2(a)",
    "",
    "**Questions, tasks, and the five accuracies (random guessing, Qwen, Phi, Llama-3.1-70B):**  ",
    "TODO",
    "",
    "**Why random guessing is a useful reference (1 sentence):**  ",
    "TODO",
])

HW5_P2B_RESPONSE = "\n".join([
    "### Your response - Problem 2(b)",
    "",
    "**Difference and McNemar p-value:**  ",
    "TODO",
    "",
    "**Paired SE, unpaired SE, and how many times wider the unpaired SE is:**  ",
    "TODO",
    "",
    "**What McNemar's test does and does not tell the team (2 sentences):**  ",
    "TODO",
])

HW5_P2C_RESPONSE = "\n".join([
    "### Your response - Problem 2(c)",
    "",
    "**1. The task that favors Phi most, and the task that favors Qwen most:**  ",
    "TODO",
    "",
    "**2. 95% task bootstrap interval:**  ",
    "TODO",
    "",
    "**3. Task bootstrap SE compared with the paired SE:**  ",
    "TODO",
    "",
    "**4. The assumption from Problem 1(a)(ii) that resampling tasks relaxes, what it assumes instead, and why the pairs stay together (2-3 sentences):**  ",
    "TODO",
])

HW5_P2D_RESPONSE = "\n".join([
    "### Your response - Problem 2(d)",
    "",
    "**1. Lower bound, and is Phi non-inferior at 3 points?**  ",
    "TODO",
    "",
    "**2. Not significant vs. non-inferior (2 sentences):**  ",
    "TODO",
    "",
    "**3. At a 1-point margin: both conclusions, which to trust, and why the margin comes first (2 sentences):**  ",
    "TODO",
    "",
    "**4. Two other costs and how each changes the recommendation, plus two costs that cannot be chosen separately:**  ",
    "TODO",
])

HW5_P2E_RESPONSE = "\n".join([
    "### Your response - Problem 2(e)",
    "",
    "**1. First half, second half, and all questions:**  ",
    "TODO",
    "",
    "**2. Why the first-half number is larger, using Problem 1(d):**  ",
    "TODO",
    "",
    "**3. Why the second-half number is still large, and what is misleading about the blog post (2 sentences):**  ",
    "TODO",
    "",
    "**4. What a fair comparison should report (1 sentence):**  ",
    "TODO",
])

HW5_P3A_RESPONSE = "\n".join([
    "### Your response - Problem 3(a)",
    "",
    "**My prompt:**  ",
    "TODO",
    "",
    "**The assistant's complete first response:**  ",
    "TODO",
])

HW5_P3B_RESPONSE = "\n".join([
    "### Your response - Problem 3(b)",
    "",
    "**My follow-up prompt with the full evidence:**  ",
    "TODO",
    "",
    "**The assistant's response:**  ",
    "TODO",
    "",
    "**What changed, and which evidence changed it (2 sentences):**  ",
    "TODO",
])

HW5_P3C_RESPONSE = "\n".join([
    "### Your response - Problem 3(c)",
    "",
    "**My recommendation (2-3 sentences):**  ",
    "TODO",
    "",
    "**One claim from an AI response that the evidence does not support:**  ",
    "TODO",
])

HW5_AI_RECORD = HW4_AI_RECORD


HW6_P1_RESPONSES = {
    "a": _hw4_p1_response("a", ["(i)", "(ii)", "(iii)"]),
    "b": _hw4_p1_response("b", ["(i) 1.", "(i) 2.", "(i) 3.", "(i) 4.", "(i) 5.", "(ii)", "(iii)"]),
    "c": _hw4_p1_response("c", ["(i)", "(ii)", "(iii)", "(iv)"]),
    "d": _hw4_p1_response("d", ["(i)", "(ii) 1.", "(ii) 2.", "(ii) 3.", "(iii)"]),
}

HW6_P2A_CODE = "\n".join([
    "# Problem 2(a), step 1: four patches without tumor, then four with tumor, from each hospital (as in Lab 9)",
    "fig, axes = plt.subplots(4, 8, figsize=(16, 9))",
    "for row, hospital in enumerate([1, 2, 3, 4]):",
    "    here = patches[patches[\"hospital\"] == hospital]",
    "    no_tumor = here[here[\"label\"] == 0].sample(4, random_state=SEED)",
    "    tumor = here[here[\"label\"] == 1].sample(4, random_state=SEED)",
    "    rows_here = pd.concat([no_tumor, tumor])",
    "    for col in range(8):",
    "        i = rows_here.index[col]",
    "        axes[row, col].imshow(images[i])",
    "        axes[row, col].set_title(f\"hospital {hospital}, \" + (\"tumor\" if patches.loc[i, \"label\"] == 1 else \"no tumor\"), fontsize=9)",
    "        axes[row, col].axis(\"off\")",
    "plt.tight_layout()",
    "plt.show()",
    "",
    "# Problem 2(a), step 2: the two measurements, benchmark against hospital 4",
    "# Gray and orange, so neither group's color looks like a stain color",
    "fig, axes = plt.subplots(1, 2, figsize=(12, 4))",
    "for ax, column, axis_label in [(axes[0], \"blue_minus_red\", \"blue minus red (larger is bluer)\"),",
    "                               (axes[1], \"brightness\", \"brightness (smaller is darker)\")]:",
    "    bins = np.linspace(patches[column].min(), patches[column].max(), 40)   # the same bins for both groups",
    "    ax.hist(benchmark[column], bins=bins, alpha=0.6, density=True, color=\"#8a8a85\", label=\"benchmark (hospitals 1-3)\")",
    "    ax.hist(hospital_4[column], bins=bins, alpha=0.6, density=True, color=\"#d95926\", label=\"hospital 4\")",
    "    ax.set_xlabel(axis_label)",
    "    ax.legend()",
    "plt.tight_layout()",
    "plt.show()",
    "",
    "# Problem 2(a), step 3: how much of hospital 4 lies outside the benchmark's range",
    "for column in [\"blue_minus_red\", \"brightness\"]:",
    "    below = (hospital_4[column] < benchmark[column].min()).mean()",
    "    above = (hospital_4[column] > benchmark[column].max()).mean()",
    "    print(f\"{column}: benchmark mean {benchmark[column].mean():.1f}, hospital 4 mean {hospital_4[column].mean():.1f}\")",
    "    print(f\"    hospital 4 patches below the benchmark's range: {below:.1%}, above it: {above:.1%}\")",
    "",
    "# The benchmark's darkest third is every patch below the benchmark's 1/3 point of brightness",
    "darkest_third_cut = np.quantile(benchmark[\"brightness\"], 1 / 3)",
    "print(f\"Hospital 4 patches in the benchmark's darkest third: {(hospital_4['brightness'] < darkest_third_cut).mean():.1%}\")",
])

HW6_P2C_CODE = "\n".join([
    "# Problem 2(c): reweight the benchmark's accuracy to hospital 4 in five ways",
    "",
    "# Lab 9's two functions, unchanged",
    "def accuracy_by_group(groups, correct):",
    "    \"\"\"One row per group: cases, the benchmark's share, and accuracy with a Wilson interval.\"\"\"",
    "    table = pd.DataFrame({\"group\": groups, \"correct\": correct})",
    "    total = len(table)",
    "    rows = []",
    "    for group_name, cases in table.groupby(\"group\"):",
    "        n = len(cases)                       # cases in this group",
    "        right = int(cases[\"correct\"].sum())  # cases the model got right",
    "        low, high = proportion_confint(right, n, method=\"wilson\")",
    "        rows.append({\"group\": group_name, \"cases\": n, \"benchmark_share\": n / total,",
    "                     \"accuracy\": right / n, \"ci_low\": low, \"ci_high\": high})",
    "    return pd.DataFrame(rows).sort_values(\"accuracy\").reset_index(drop=True)",
    "",
    "",
    "def reweight(by_group, shares):",
    "    \"\"\"Accuracy for a mix of groups, its standard error, and Kish's effective sample size.\"\"\"",
    "    total_share = sum(shares.values())",
    "    estimate = 0.0",
    "    variance = 0.0",
    "    weight_sum = 0.0",
    "    for _, row in by_group.iterrows():",
    "        share = shares.get(row[\"group\"], 0.0) / total_share  # shares are rescaled to add to 1",
    "        p = row[\"accuracy\"]",
    "        n = row[\"cases\"]",
    "        estimate = estimate + share * p                   # share times accuracy, added up as in the table",
    "        variance = variance + share**2 * p * (1 - p) / n  # each group's variance, times its share squared",
    "        weight_sum = weight_sum + share**2 / n            # used for Kish's effective sample size",
    "    return estimate, np.sqrt(variance), 1 / weight_sum",
    "",
    "",
    "# Part 1: you fill in the arguments marked TODO in groups_for() below.",
    "TODO = None",
    "",
    "",
    "def cut_into_groups(column, n_groups, data):",
    "    \"\"\"Cut a measurement at the benchmark's quantiles and name each patch's group.\"\"\"",
    "    if column is None or n_groups is None:",
    "        raise ValueError(\"Fill in the column and the number of groups in every call in groups_for(), then run this cell again.\")",
    "    cut_points = np.quantile(benchmark[column], np.linspace(0, 1, n_groups + 1)[1:-1])",
    "    numbers = np.digitize(data[column], cut_points) + 1   # 1 is the lowest group",
    "    names = []",
    "    for number in numbers:",
    "        names.append(f\"{column} {number} of {n_groups}\")",
    "    return np.array(names)",
    "",
    "",
    "def groups_for(specification, data):",
    "    \"\"\"The group of every patch in data under one specification of Z.",
    "",
    "    Part 1: replace each TODO with the column (\"blue_minus_red\" or \"brightness\")",
    "    and the number of groups (3 or 5) for that specification.",
    "    \"\"\"",
    "    if specification == \"0. primary: color thirds\":",
    "        return cut_into_groups(TODO, TODO, data)",
    "    if specification == \"1. color fifths\":",
    "        return cut_into_groups(TODO, TODO, data)",
    "    if specification == \"2. brightness thirds\":",
    "        return cut_into_groups(TODO, TODO, data)",
    "    if specification == \"3. brightness fifths\":",
    "        return cut_into_groups(TODO, TODO, data)",
    "    if specification == \"4. color thirds and brightness thirds\":",
    "        color = cut_into_groups(TODO, TODO, data)   # the color group, as in 0",
    "        dark = cut_into_groups(TODO, TODO, data)    # the brightness group, as in 2",
    "        names = []",
    "        for i in range(len(color)):",
    "            names.append(color[i] + \" / \" + dark[i])",
    "        return np.array(names)",
    "",
    "",
    "def hospital_4_shares(groups):",
    "    \"\"\"Hospital 4's share of patches in each group. These need no labels.\"\"\"",
    "    shares = {}",
    "    for name in np.unique(groups):",
    "        shares[name] = np.mean(groups == name)",
    "    return shares",
    "",
    "",
    "specifications = [\"0. primary: color thirds\", \"1. color fifths\", \"2. brightness thirds\",",
    "                  \"3. brightness fifths\", \"4. color thirds and brightness thirds\"]",
    "",
    "rows = []",
    "for specification in specifications:",
    "    benchmark_groups = groups_for(specification, benchmark)",
    "    by_group = accuracy_by_group(benchmark_groups, benchmark[\"correct\"].to_numpy())",
    "    shares = hospital_4_shares(groups_for(specification, hospital_4))",
    "",
    "    # Overlap check: a hospital 4 group with no benchmark patches cannot be reweighted.",
    "    for name in shares:",
    "        if name not in list(by_group[\"group\"]):",
    "            print(\"No benchmark patches in\", name, \"- hospital 4 share\", round(shares[name], 3))",
    "",
    "    estimate, se, n_eff = reweight(by_group, shares)",
    "    rows.append({\"specification\": specification, \"groups\": len(by_group),",
    "                 \"estimate\": estimate, \"se\": se, \"n_eff\": n_eff})",
    "",
    "table = pd.DataFrame(rows)",
    "",
    "# Part 3 (TODO): the one-sided 95% lower bound, estimate - 1.645 * se",
    "table[\"lower_bound\"] = np.nan",
    "# Part 3 (TODO): the decision, \"use\" or \"do not use\", under the rule: use the model if the lower bound is at least 0.85",
    "table[\"decision\"] = \"TODO\"",
    "display(table.round(3))",
    "",
    "# Part 4: the five estimates with 95% intervals, in the order listed",
    "fig, ax = plt.subplots(figsize=(8, 3.5))",
    "y = np.arange(len(table))[::-1]   # the primary analysis at the top",
    "ax.errorbar(table[\"estimate\"], y, xerr=1.96 * table[\"se\"], fmt=\"o\", color=\"#155a8a\", capsize=0)",
    "ax.axvline(0.85, color=\"#c41230\", linestyle=\"--\", label=\"0.85, the pathology lead's line\")",
    "ax.set_yticks(y)",
    "ax.set_yticklabels(table[\"specification\"])",
    "ax.set_xlabel(\"reweighted accuracy for hospital 4 (95% interval)\")",
    "ax.legend(loc=\"upper right\")",
    "plt.tight_layout()",
    "plt.show()",
    "",
    "# Part 5: alternative 4's nine groups, one row per group",
    "nine_groups = \"4. color thirds and brightness thirds\"",
    "cells = pd.DataFrame({\"benchmark patches\": pd.Series(groups_for(nine_groups, benchmark)).value_counts(),",
    "                      \"hospital 4 patches\": pd.Series(groups_for(nine_groups, hospital_4)).value_counts()})",
    "display(cells.fillna(0).astype(int).sort_values(\"hospital 4 patches\", ascending=False))",
])

HW6_P2D_CODE = "\n".join([
    "# Problem 2(d), part 1: hospital 4's own labels",
    "print(f\"Hospital 4 accuracy: {hospital_4['correct'].mean():.3f} ({hospital_4['correct'].sum()} of {len(hospital_4)} patches)\")",
    "print(f\"Benchmark accuracy:  {benchmark['correct'].mean():.3f}\")",
    "",
    "",
    "# Lab 9's slide bootstrap for a difference in accuracy, unchanged",
    "def slide_bootstrap_difference(new, old, B=4000, seed=SEED):",
    "    \"\"\"Percentile interval for accuracy(new) - accuracy(old), resampling whole slides in each.\"\"\"",
    "    rng = np.random.default_rng(seed)",
    "    # Keep each slide's patches together: one array of 0s and 1s per slide",
    "    new_slides = []",
    "    for _, cases in new.groupby(\"slide_id\"):",
    "        new_slides.append(cases[\"correct\"].to_numpy())",
    "    old_slides = []",
    "    for _, cases in old.groupby(\"slide_id\"):",
    "        old_slides.append(cases[\"correct\"].to_numpy())",
    "    differences = []",
    "    for b in range(B):",
    "        # Draw as many slides as each place has, with replacement",
    "        new_pick = rng.integers(0, len(new_slides), len(new_slides))",
    "        old_pick = rng.integers(0, len(old_slides), len(old_slides))",
    "        # Pool the patches on the drawn slides and compute each accuracy",
    "        new_accuracy = np.concatenate([new_slides[i] for i in new_pick]).mean()",
    "        old_accuracy = np.concatenate([old_slides[i] for i in old_pick]).mean()",
    "        differences.append(new_accuracy - old_accuracy)",
    "    # The middle 95% of the 4,000 differences",
    "    return np.percentile(differences, [2.5, 97.5])",
    "",
    "",
    "low, high = slide_bootstrap_difference(hospital_4, benchmark)",
    "print(f\"Hospital 4 minus benchmark: {hospital_4['correct'].mean() - benchmark['correct'].mean():+.3f} \"",
    "      f\"(95% interval {low:+.3f} to {high:+.3f}, resampling slides)\")",
    "",
    "# Problem 2(d), part 2: accuracy within each brightness third",
    "benchmark_dark = cut_into_groups(\"brightness\", 3, benchmark)",
    "hospital_4_dark = cut_into_groups(\"brightness\", 3, hospital_4)",
    "rows = []",
    "for name in np.unique(benchmark_dark):",
    "    in_benchmark = benchmark_dark == name",
    "    in_hospital_4 = hospital_4_dark == name",
    "    rows.append({\"brightness group\": name,",
    "                 \"benchmark patches\": in_benchmark.sum(),",
    "                 \"benchmark accuracy\": benchmark[\"correct\"].to_numpy()[in_benchmark].mean(),",
    "                 \"hospital 4 patches\": in_hospital_4.sum(),",
    "                 \"hospital 4 accuracy\": hospital_4[\"correct\"].to_numpy()[in_hospital_4].mean()})",
    "display(pd.DataFrame(rows).round(3))",
    "",
    "",
    "# Problem 2(d), part 3: resample whole slides for the primary analysis",
    "def slide_bootstrap_reweighted(specification, B=2000, seed=SEED):",
    "    \"\"\"B reweighted estimates, each from benchmark slides and hospital 4 slides drawn with replacement.\"\"\"",
    "    rng = np.random.default_rng(seed)",
    "    benchmark_slides = []",
    "    for _, cases in benchmark.groupby(\"slide_id\"):",
    "        benchmark_slides.append(cases)",
    "    hospital_4_slides = []",
    "    for _, cases in hospital_4.groupby(\"slide_id\"):",
    "        hospital_4_slides.append(cases)",
    "",
    "    estimates = []",
    "    for b in range(B):",
    "        # Draw as many slides as each place has, with replacement",
    "        benchmark_pick = rng.integers(0, len(benchmark_slides), len(benchmark_slides))",
    "        hospital_4_pick = rng.integers(0, len(hospital_4_slides), len(hospital_4_slides))",
    "        benchmark_sample = pd.concat([benchmark_slides[i] for i in benchmark_pick])",
    "        hospital_4_sample = pd.concat([hospital_4_slides[i] for i in hospital_4_pick])",
    "",
    "        # Redo the reweighting on the resampled patches, with the same cut points",
    "        by_group = accuracy_by_group(groups_for(specification, benchmark_sample),",
    "                                     benchmark_sample[\"correct\"].to_numpy())",
    "        shares = hospital_4_shares(groups_for(specification, hospital_4_sample))",
    "        estimate, se, n_eff = reweight(by_group, shares)",
    "        estimates.append(estimate)",
    "    return np.array(estimates)",
    "",
    "",
    "reweighted_estimates = slide_bootstrap_reweighted(\"0. primary: color thirds\")   # takes a few seconds",
    "print(\"Primary analysis, resampling slides\")",
    "print(\"  95% interval:\", np.round(np.quantile(reweighted_estimates, [0.025, 0.975]), 3))",
    "print(\"  one-sided 95% lower bound (the 5th percentile):\", round(np.quantile(reweighted_estimates, 0.05), 3))",
])

HW6_P2A_RESPONSE = "\n".join([
    "### Your response - Problem 2(a)",
    "",
    "**1. How hospital 4's patches differ from the benchmark's (2-3 sentences):**  ",
    "TODO",
    "",
    "**2. Share outside the benchmark's range on each measure, and share in the benchmark's darkest third:**  ",
    "TODO",
])

HW6_P2B_RESPONSE = "\n".join([
    "### Your response - Problem 2(b)",
    "",
    "Fill in this table and save the notebook **before** you run part (c).",
    "",
    "| Alternative | What it changes about Z, compared with the primary | Why it is a reasonable choice | Higher or lower than the primary's estimate? | Will the decision change? |",
    "|---|---|---|---|---|",
    "| 1. color fifths | TODO | TODO | TODO | TODO |",
    "| 2. brightness thirds | TODO | TODO | TODO | TODO |",
    "| 3. brightness fifths | TODO | TODO | TODO | TODO |",
    "| 4. color thirds and brightness thirds (9 groups) | TODO | TODO | TODO | TODO |",
    "",
    "**The alternative most likely to change the decision, and why:**  ",
    "TODO",
])

HW6_P2C_RESPONSE = "\n".join([
    "### Your response - Problem 2(c)",
    "",
    "**1.** Fill in the arguments marked `TODO` in `groups_for()` in the code cell above.",
    "",
    "**2. What `cut_into_groups()` does, what the loop computes for each specification, and which numbers use labels (3-4 sentences):**  ",
    "TODO",
    "",
    "**3.** Fill in the `lower_bound` and `decision` columns in the code cell above.",
    "",
    "**4. Which specification, if any, changes the decision:**  ",
    "TODO",
    "",
    "**5. Why the effective sample size falls as Z gets finer, and the group with the most hospital 4 patches:**  ",
    "TODO",
    "",
    "**6. Which of your predictions in (b) came true, and which did not:**  ",
    "TODO",
])

HW6_P2D_RESPONSE = "\n".join([
    "### Your response - Problem 2(d)",
    "",
    "**1. Hospital 4's accuracy, its difference from the benchmark with the slide interval, and whether any specification predicted it:**  ",
    "TODO",
    "",
    "**2. Which assumption failed, and how the brightness table shows it:**  ",
    "TODO",
    "",
    "**3. The slide-resampled lower bound, and whether it would have warned hospital 4:**  ",
    "TODO",
    "",
    "**4. What is wrong with reporting the specification closest to the labels (2 sentences):**  ",
    "TODO",
])

HW6_P2E_RESPONSE = "\n".join([
    "### Your response - Problem 2(e)",
    "",
    "**A paragraph for hospital 4's pathology lead (3-5 sentences, with every item in the list):**  ",
    "TODO",
])

HW6_P3A_RESPONSE = "\n".join([
    "### Your response - Problem 3(a)",
    "",
    "**My prompt:**  ",
    "TODO",
    "",
    "**The assistant's complete response:**  ",
    "TODO",
    "",
    "| Suggestion | Sensitivity analysis, model shopping, or either | Statistical reason |",
    "|---|---|---|",
    "| 1. TODO | TODO | TODO |",
    "| 2. TODO | TODO | TODO |",
    "| 3. TODO | TODO | TODO |",
])

HW6_P3B_RESPONSE = "\n".join([
    "### Your response - Problem 3(b)",
    "",
    "**The most misleading suggestion and the problem with it, or why none is misleading (2-3 sentences):**  ",
    "TODO",
])

HW6_P3C_RESPONSE = "\n".join([
    "### Your response - Problem 3(c)",
    "",
    "**Primary analysis:**  ",
    "TODO",
    "",
    "**One alternative, and why it is reasonable:**  ",
    "TODO",
    "",
    "**The rule that turns the results into a decision:**  ",
    "TODO",
    "",
    "**What I will report if the alternative gives a different decision:**  ",
    "TODO",
])

HW6_AI_RECORD = HW4_AI_RECORD

HW7_STARTER = '''# Read MT-Bench's judgments and keep this homework's half of the questions
judge_dir = data_dir / "llm_judges"
items = pd.read_csv(judge_dir / "items.csv")
votes = pd.read_csv(judge_dir / "human_votes.csv")
questions = pd.read_csv(judge_dir / "questions.csv", keep_default_na=False)
answers = pd.read_csv(judge_dir / "answers.csv", keep_default_na=False)   # one answer is empty; keep it as ""

items = items[items["half"] == "homework"].reset_index(drop=True)   # math, coding, extraction, humanities
votes = votes.merge(items, on="item_id")                             # one row per expert vote, with its item's details
print(f"{len(items):,} items from {items['question_id'].nunique()} questions in {items['category'].nunique()} categories")
print(f"{len(votes):,} expert votes from {votes['judge'].nunique()} experts; {(items['n_human_votes'] >= 2).sum()} items have 2 or more")


def answer_of(question_id, model, turn):
    """One model's reply to one turn of one question."""
    row = answers[(answers["question_id"] == question_id) & (answers["model"] == model) & (answers["turn"] == turn)]
    return row["answer"].iloc[0]


# Items from one question are related, so every interval resamples questions.
question_ids = np.array(sorted(items["question_id"].unique()))
'''

HW7_P1_RESPONSES = {
    "a": _hw4_p1_response("a", ["(i)", "(ii)", "(iii)"]),
    "b": _hw4_p1_response("b", ["Agreement, chance agreement, and kappa", "Why agreement alone is a poor summary"]),
    "c": _hw4_p1_response("c", ["(i)", "(ii)", "(iii)", "(iv)"]),
    "d": _hw4_p1_response("d", ["(i)", "(ii)", "(iii)"]),
    "e": _hw4_p1_response("e", ["(i)", "(ii)", "(iii)"]),
}

HW7_P2A_CODE = '''# Problem 2(a): two items where the experts split between the two models
def show_item(item_id, characters=1000):
    """Print an item's question, both answers (cut at `characters`), the expert votes, and GPT-4's verdict."""
    item = items[items["item_id"] == item_id].iloc[0]
    question = questions[questions["question_id"] == item["question_id"]].iloc[0]
    print(f"Item {item_id}: question {item['question_id']} ({item['category']}), turn {item['turn']}")
    if item["turn"] == 2:
        print("The user's first message:", question["turn_1"][:characters])
    print("The message being answered:", question[f"turn_{item['turn']}"][:characters])
    for label in ["model_1", "model_2"]:
        print(f"\\n--- {label}: {item[label]} ---")
        print(answer_of(item["question_id"], item[label], item["turn"])[:characters])
    print("\\nExpert votes:", votes[votes["item_id"] == item_id]["vote"].tolist())
    agreed = "the two orders agreed" if item["gpt4_orders_agree"] else "the two orders disagreed"
    print(f"GPT-4: {item['gpt4_verdict']} ({agreed})")
    print("=" * 80)


vote_sets = votes.groupby("item_id")["vote"].agg(set)
split_items = sorted(i for i, s in vote_sets.items() if {"model_1", "model_2"} <= s)
print(len(split_items), "items have votes for both models")
looked_at = np.random.default_rng(SEED).choice(split_items, size=2, replace=False)
for item_id in looked_at:
    show_item(item_id)
'''

HW7_P2B_CODE = '''# Problem 2(b): agreement corrected for chance, expert with expert and GPT-4 with expert
CATEGORIES = ["model_1", "model_2", "tie"]


def kappa(first, second, pooled=False):
    """Observed agreement, chance agreement, and kappa for two equally long lists of votes."""
    first, second = np.asarray(first), np.asarray(second)
    observed = np.mean(first == second)
    if pooled:
        # Two experts on the same item are interchangeable, so both use the shares of all their votes together.
        shares = pd.Series(np.concatenate([first, second])).value_counts(normalize=True)
        share_first, share_second = shares, shares
    else:
        # GPT-4 and the experts each have their own shares.
        share_first = pd.Series(first).value_counts(normalize=True)
        share_second = pd.Series(second).value_counts(normalize=True)
    # TODO (Problem 2(b)1): the chance agreement, as in Problem 1(a) but with three categories.
    # For a category c, share_first.get(c, 0) is the first rater's share of votes for c.
    chance = None
    if chance is None:
        raise NotImplementedError("Finish the chance-agreement line in kappa() (Problem 2(b)1), then run this cell again.")
    return observed, chance, (observed - chance) / (1 - chance)


# Every pair of experts who judged the same item
rows = []
for item_id, group in votes.groupby("item_id"):
    item_votes = group["vote"].tolist()
    for i in range(len(item_votes)):
        for j in range(i + 1, len(item_votes)):
            rows.append({"item_id": item_id, "question_id": group["question_id"].iloc[0],
                         "first": item_votes[i], "second": item_votes[j]})
expert_pairs = pd.DataFrame(rows)


def kappa_experts(pairs):
    return kappa(pairs["first"], pairs["second"], pooled=True)


def kappa_gpt4(expert_votes):
    return kappa(expert_votes["gpt4_verdict"], expert_votes["vote"])


def resample_kappas(pairs, expert_votes, B=2000, seed=SEED):
    """Kappa for experts, kappa for GPT-4, and their difference, resampling whole questions B times."""
    rng = np.random.default_rng(seed)
    pair_parts = {q: part for q, part in pairs.groupby("question_id")}
    vote_parts = {q: part for q, part in expert_votes.groupby("question_id")}
    ids = np.array(sorted(vote_parts))
    results = []
    for _ in range(B):
        drawn = rng.choice(ids, size=len(ids), replace=True)
        k_experts = kappa_experts(pd.concat([pair_parts[q] for q in drawn if q in pair_parts]))[2]
        k_gpt4 = kappa_gpt4(pd.concat([vote_parts[q] for q in drawn]))[2]
        results.append((k_experts, k_gpt4, k_gpt4 - k_experts))
    return np.array(results)


resampled = resample_kappas(expert_pairs, votes)
table = []
for column, (name, data, statistic) in enumerate([("expert with expert", expert_pairs, kappa_experts),
                                                   ("GPT-4 with expert", votes, kappa_gpt4)]):
    observed, chance, k = statistic(data)
    low, high = np.percentile(resampled[:, column], [2.5, 97.5])
    table.append({"comparison": name, "n": len(data), "agreement": observed, "chance": chance,
                  "kappa": k, "2.5%": low, "97.5%": high})
display(pd.DataFrame(table).round(3))
low, high = np.percentile(resampled[:, 2], [2.5, 97.5])
print(f"Difference in kappa, GPT-4 minus experts: {table[1]['kappa'] - table[0]['kappa']:+.3f} (95% interval {low:+.3f} to {high:+.3f})")
print(f"{expert_pairs['item_id'].nunique()} items have a pair of experts, from {expert_pairs['question_id'].nunique()} questions")
'''

HW7_P2C_CODE = '''# Problem 2(c): the same comparison within each category (10 questions each)
rows = []
for category in sorted(items["category"].unique()):
    category_pairs = expert_pairs[expert_pairs["item_id"].isin(items.loc[items["category"] == category, "item_id"])]
    category_votes = votes[votes["category"] == category]
    k_experts = kappa_experts(category_pairs)[2]
    k_gpt4 = kappa_gpt4(category_votes)[2]
    low, high = np.percentile(resample_kappas(category_pairs, category_votes, B=1000)[:, 2], [2.5, 97.5])
    rows.append({"category": category, "questions": category_votes["question_id"].nunique(),
                 "expert pairs": len(category_pairs), "expert votes": len(category_votes),
                 "expert kappa": k_experts, "GPT-4 kappa": k_gpt4,
                 "difference": k_gpt4 - k_experts, "2.5%": low, "97.5%": high})
by_category = pd.DataFrame(rows)
display(by_category.round(3))

# The difference in kappa for each category, with its interval and a line at 0
fig, ax = plt.subplots(figsize=(7, 3))
y = np.arange(len(by_category))
ax.hlines(y, by_category["2.5%"], by_category["97.5%"], color="#5b8db8", linewidth=3)
ax.plot(by_category["difference"], y, "o", color="#155a8a")
ax.axvline(0, color="#333333", linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(by_category["category"])
ax.set_xlabel("GPT-4's kappa minus the experts' kappa, with 95% interval")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.show()
'''

HW7_P2D_CODE = '''# Problem 2(d): how often GPT-4's two orders disagree, and how that depends on the pair of models
flipped = ~items["gpt4_orders_agree"]
flip_rate = flipped.mean()
naive_se = np.sqrt(flip_rate * (1 - flip_rate) / len(items))    # as if the 1,200 items were independent

rng = np.random.default_rng(SEED)
flip_parts = {q: part["gpt4_orders_agree"].to_numpy() for q, part in items.groupby("question_id")}
resampled_flips = []
for _ in range(2000):
    drawn = rng.choice(question_ids, size=len(question_ids), replace=True)
    resampled_flips.append(1 - np.concatenate([flip_parts[q] for q in drawn]).mean())
low, high = np.percentile(resampled_flips, [2.5, 97.5])
print(f"GPT-4's orders disagree on {flipped.sum()} of {len(items)} items: {flip_rate:.3f} (95% interval {low:.3f} to {high:.3f})")
print(f"SE resampling questions {np.std(resampled_flips):.4f}; as if items were independent {naive_se:.4f}; design effect {(np.std(resampled_flips) / naive_se) ** 2:.2f}")

# Each model's strength: its share of the expert votes it took part in, counting a tie as half a win
wins = pd.concat([
    votes.assign(model=votes["model_1"], won=(votes["vote"] == "model_1") + 0.5 * (votes["vote"] == "tie")),
    votes.assign(model=votes["model_2"], won=(votes["vote"] == "model_2") + 0.5 * (votes["vote"] == "tie")),
])
strength = wins.groupby("model")["won"].mean().sort_values()
print("\\nEach model's share of expert votes won (a tie counts as half):")
print(strength.round(3).to_string())
rank = {model: position for position, model in enumerate(strength.index, start=1)}
items["rank gap"] = (items["model_1"].map(rank) - items["model_2"].map(rank)).abs()
votes["rank gap"] = votes["item_id"].map(items.set_index("item_id")["rank gap"])

by_gap = pd.DataFrame({
    "items": items.groupby("rank gap").size(),
    "flip rate": 1 - items.groupby("rank gap")["gpt4_orders_agree"].mean(),
    "expert votes": votes.groupby("rank gap").size(),
    "GPT-4 agrees with expert": (votes["gpt4_verdict"] == votes["vote"]).groupby(votes["rank gap"]).mean(),
})
display(by_gap.round(3))
'''

HW7_P2E_CODE = '''# Problem 2(e): how often a verdict for one answer goes to the longer answer
length = answers.assign(chars=answers["answer"].str.len()).set_index(["question_id", "model", "turn"])["chars"]


def longer_share(table, verdict_column):
    """Among verdicts that pick a winner (answers of different lengths), the share that pick the longer answer."""
    length_1 = np.array([length[(q, m, t)] for q, m, t in zip(table["question_id"], table["model_1"], table["turn"])])
    length_2 = np.array([length[(q, m, t)] for q, m, t in zip(table["question_id"], table["model_2"], table["turn"])])
    verdict = table[verdict_column].to_numpy()
    keep = np.isin(verdict, ["model_1", "model_2"]) & (length_1 != length_2)
    picked_longer = np.where(verdict == "model_1", length_1 > length_2, length_2 > length_1)
    return picked_longer[keep].mean(), keep.sum()


for name, table, column in [("experts", votes, "vote"), ("GPT-4", items, "gpt4_verdict")]:
    share, n = longer_share(table, column)
    print(f"{name}: {share:.3f} of {n} verdicts that pick a winner pick the longer answer")
'''

HW7_P2F_CODE = '''# Problem 2(f): how much of the experts' disagreement is between items, and the reliability of a panel
# Code each vote +1 (model_1), -1 (model_2), or 0 (tie), and use items with 2 or more votes.
scored = votes.assign(score=votes["vote"].map({"model_1": 1.0, "model_2": -1.0, "tie": 0.0}))
scored = scored[scored.groupby("item_id")["score"].transform("size") >= 2]
by_item = scored.groupby("item_id")["score"]
n_i = by_item.size()
N, k = n_i.sum(), len(n_i)

# One-way random-effects ANOVA: the within-item mean square estimates sigma^2,
# and the between-item mean square estimates sigma^2 + n0 * tau^2.
sigma2 = ((scored["score"] - by_item.transform("mean")) ** 2).sum() / (N - k)
between = (n_i * (by_item.mean() - scored["score"].mean()) ** 2).sum() / (k - 1)
n0 = (N - (n_i ** 2).sum() / N) / (k - 1)          # the average number of votes per item, adjusted for unequal counts
tau2 = (between - sigma2) / n0
rho = tau2 / (tau2 + sigma2)
print(f"{k} items, {N} votes: tau^2 = {tau2:.3f}, sigma^2 = {sigma2:.3f}, rho = {rho:.3f}")
for r in range(1, 6):
    print(f"  {r} expert(s) per item: reliability {r * rho / (1 + (r - 1) * rho):.3f}")
'''

HW7_P3A_CODE = '''# Problem 3(a): five assigned items (the same for everyone) and a judging prompt for each order
PROMPT = """You are judging two answers to the same question. Decide which answer is more helpful, correct, and relevant to the question. Do not let the order of the answers, their length, or their style decide for you. Reply with one line: A, B, or tie.

[Question]
{question}

[Answer A]
{answer_a}

[Answer B]
{answer_b}"""

# Turn-1 items from pairs of models close in strength (where Problem 2(d) found most flips), on which
# the experts did not all agree, short enough to paste, and not the two items from Problem 2(a).
experts_split = votes.groupby("item_id")["vote"].nunique() > 1
pool = items[(items["turn"] == 1) & (items["rank gap"] <= 2) & items["item_id"].map(experts_split).fillna(False)
             & ~items["item_id"].isin(looked_at)].copy()
pool["characters"] = [len(answer_of(q, a, 1)) + len(answer_of(q, b, 1))
                      for q, a, b in zip(pool["question_id"], pool["model_1"], pool["model_2"])]
assigned = pool[pool["characters"] <= 2500].sample(5, random_state=SEED).sort_values("item_id")
order_rng = np.random.default_rng(SEED + 3)
assigned["run first"] = order_rng.choice(["model_1 as A", "model_2 as A"], size=len(assigned))
display(assigned[["item_id", "category", "model_1", "model_2", "run first"]])

for _, item in assigned.iterrows():
    question = questions.loc[questions["question_id"] == item["question_id"], "turn_1"].iloc[0]
    answer_1 = answer_of(item["question_id"], item["model_1"], 1)
    answer_2 = answer_of(item["question_id"], item["model_2"], 1)
    print("#" * 80)
    print(f"Item {item['item_id']}. Run first: {item['run first']}")
    print("\\n--- Prompt with model_1 as A ---\\n")
    print(PROMPT.format(question=question, answer_a=answer_1, answer_b=answer_2))
    print("\\n--- Prompt with model_2 as A ---\\n")
    print(PROMPT.format(question=question, answer_a=answer_2, answer_b=answer_1))
'''

HW7_P3C_CODE = '''# Problem 3(c): the experts' votes and GPT-4's cached verdicts for the five assigned items
reveal = assigned[["item_id", "category", "model_1", "model_2", "gpt4_verdict", "gpt4_orders_agree"]].copy()
reveal["expert votes"] = [votes.loc[votes["item_id"] == i, "vote"].tolist() for i in reveal["item_id"]]
display(reveal)
'''

HW7_P2A_RESPONSE = """### Your response - Problem 2(a)

**What the experts might be disagreeing about (2-3 sentences):**
TODO
"""

HW7_P2B_RESPONSE = """### Your response - Problem 2(b)

**1.** Finish the chance-agreement line in `kappa()` in the code cell above.

**2. The table** (agreement, chance agreement, kappa and its 95% interval for each comparison, and the difference with its interval):
TODO

**3. Why the interval resamples questions:**
TODO

**4. Can GPT-4 stand in for one expert? (2 sentences, citing the interval for the difference):**
TODO
"""

HW7_P2C_RESPONSE = """### Your response - Problem 2(c)

**1. The pattern across categories, with denominators:**
TODO

**2. How firmly you can claim it, and the connection to the winner's curse:**
TODO
"""

HW7_P2D_RESPONSE = """### Your response - Problem 2(d)

**1. Flip rate, interval, design effect, and why the design effect is above 1:**
TODO

**2. How flips and agreement change with the rank gap, and why close comparisons may be harder:**
TODO

**3. What a client comparing models one rank apart should expect, and what it says about the overall figure:**
TODO
"""

HW7_P2E_RESPONSE = """### Your response - Problem 2(e)

**1. The share for experts and for GPT-4:**
TODO

**2. How two judges can agree without either being right, and what would check a verdict (2 sentences):**
TODO
"""

HW7_P2F_RESPONSE = """### Your response - Problem 2(f)

**A paragraph for the benchmark team (3-5 sentences):**
TODO

**Design table for a follow-up study in which experts label new items:**

| Design term | Your study |
|---|---|
| Unit | TODO |
| Treatments | TODO |
| Held constant | TODO |
| Block | TODO |
| Related groups | TODO |
| Randomization | TODO |
| Response | TODO |
| Number of items and experts per item, with a reason | TODO |
"""

HW7_P2G_RESPONSE = """### Your response - Problem 2(g), stretch

**Your rule for the panel's verdict (including ties), stated before running anything:**
TODO

**Your code (in a code cell below this one) and what it found:**
TODO

**What you find, explained with Problem 1(c):**
TODO
"""

HW7_P3A_RESPONSE = """### Your response - Problem 3(a)

**My prediction, recorded before running any AI: the item most likely to flip, and why:**
TODO
"""

HW7_P3B_RESPONSE = """### Your response - Problem 3(b)

**Assistant and version:** TODO

| Item | Run first | Verdict with model_1 as A | Verdict with model_2 as A | Same model both times? |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

Translate each verdict to the model it picked: with model_1 as A, "A" means model_1; with model_2 as A, "A" means model_2.
"""

HW7_P3C_RESPONSE = """### Your response - Problem 3(c)

**What your 10 calls showed (2 sentences):**
TODO

**For the benchmark team: what a study would need before it trusts your assistant as a judge (one paragraph, 5-7 sentences, one idea from each week):**
TODO

Check that your paragraph covers each week:

| Week | The idea you used |
|---|---|
| 4: the unit and the sample size (how many items for an SE of about 0.03, and what clustering does) | TODO |
| 5 and 12: the comparison with a second rater | TODO |
| 9: whether the result carries over | TODO |
| 11: the design (held constant, randomized) | TODO |
| 12: the order of the answers | TODO |
"""

HW7_AI_RECORD = HW4_AI_RECORD

STARTER_LINES["hw07"] = HW7_STARTER.rstrip("\n").splitlines()


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
    ("hw04", "2", "a"): HW4_P2A_RESPONSE,
    ("hw04", "2", "b"): HW4_P2B_RESPONSE,
    ("hw04", "2", "c"): HW4_P2C_RESPONSE,
    ("hw04", "3", "a"): HW4_P3A_RESPONSE,
    ("hw04", "3", "b"): HW4_P3B_RESPONSE,
    ("hw05", "1", "a"): HW5_P1_RESPONSES["a"],
    ("hw05", "1", "b"): HW5_P1_RESPONSES["b"],
    ("hw05", "1", "c"): HW5_P1_RESPONSES["c"],
    ("hw05", "1", "d"): HW5_P1_RESPONSES["d"],
    ("hw05", "2", "a"): HW5_P2A_RESPONSE,
    ("hw05", "2", "b"): HW5_P2B_RESPONSE,
    ("hw05", "2", "c"): HW5_P2C_RESPONSE,
    ("hw05", "2", "d"): HW5_P2D_RESPONSE,
    ("hw05", "2", "e"): HW5_P2E_RESPONSE,
    ("hw05", "3", "a"): HW5_P3A_RESPONSE,
    ("hw05", "3", "b"): HW5_P3B_RESPONSE,
    ("hw05", "3", "c"): HW5_P3C_RESPONSE,
    ("hw06", "1", "a"): HW6_P1_RESPONSES["a"],
    ("hw06", "1", "b"): HW6_P1_RESPONSES["b"],
    ("hw06", "1", "c"): HW6_P1_RESPONSES["c"],
    ("hw06", "1", "d"): HW6_P1_RESPONSES["d"],
    ("hw06", "2", "a"): HW6_P2A_RESPONSE,
    ("hw06", "2", "b"): HW6_P2B_RESPONSE,
    ("hw06", "2", "c"): HW6_P2C_RESPONSE,
    ("hw06", "2", "d"): HW6_P2D_RESPONSE,
    ("hw06", "2", "e"): HW6_P2E_RESPONSE,
    ("hw06", "3", "a"): HW6_P3A_RESPONSE,
    ("hw06", "3", "b"): HW6_P3B_RESPONSE,
    ("hw06", "3", "c"): HW6_P3C_RESPONSE,
    ("hw07", "1", "a"): HW7_P1_RESPONSES["a"],
    ("hw07", "1", "b"): HW7_P1_RESPONSES["b"],
    ("hw07", "1", "c"): HW7_P1_RESPONSES["c"],
    ("hw07", "1", "d"): HW7_P1_RESPONSES["d"],
    ("hw07", "1", "e"): HW7_P1_RESPONSES["e"],
    ("hw07", "2", "a"): HW7_P2A_RESPONSE,
    ("hw07", "2", "b"): HW7_P2B_RESPONSE,
    ("hw07", "2", "c"): HW7_P2C_RESPONSE,
    ("hw07", "2", "d"): HW7_P2D_RESPONSE,
    ("hw07", "2", "e"): HW7_P2E_RESPONSE,
    ("hw07", "2", "f"): HW7_P2F_RESPONSE,
    ("hw07", "2", "g"): HW7_P2G_RESPONSE,
    ("hw07", "3", "a"): HW7_P3A_RESPONSE,
    ("hw07", "3", "b"): HW7_P3B_RESPONSE,
    ("hw07", "3", "c"): HW7_P3C_RESPONSE,
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
    ("hw05", "2", "a"): HW5_P2A_CODE,
    ("hw05", "2", "b"): HW5_P2B_CODE,
    ("hw05", "2", "c"): HW5_P2C_CODE,
    ("hw05", "2", "d"): HW5_P2D_CODE,
    ("hw05", "2", "e"): HW5_P2E_CODE,
    ("hw06", "2", "a"): HW6_P2A_CODE,
    ("hw06", "2", "c"): HW6_P2C_CODE,
    ("hw06", "2", "d"): HW6_P2D_CODE,
    ("hw07", "2", "a"): HW7_P2A_CODE,
    ("hw07", "2", "b"): HW7_P2B_CODE,
    ("hw07", "2", "c"): HW7_P2C_CODE,
    ("hw07", "2", "d"): HW7_P2D_CODE,
    ("hw07", "2", "e"): HW7_P2E_CODE,
    ("hw07", "2", "f"): HW7_P2F_CODE,
    ("hw07", "3", "a"): HW7_P3A_CODE,
    ("hw07", "3", "c"): HW7_P3C_CODE,
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
    subpart_pattern = {"hw03": r"(?=^[a-f]\.\s)", "hw07": r"(?=^[a-g]\.\s)"}.get(hw_id, r"(?=^[a-e]\.\s)")
    pieces = re.split(subpart_pattern, body, flags=re.M)
    introduction = pieces[0].strip()
    cells = [markdown_cell(heading + ("\n\n" + introduction if introduction else ""))]
    if len(pieces) == 1:
        cells.append(markdown_cell(RESPONSE.format(label=heading.replace("# ", ""))))
        return cells
    problem_number = re.search(r"Problem (\d+)", heading).group(1)
    for piece in pieces[1:]:
        piece = piece.strip()
        letter = re.match(r"([a-g])\.", piece).group(1)
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
        code_cell(build_simple_setup(DATA_GROUPS[hw_id])),
        code_cell(build_common_imports()),
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
    if hw_id in ("hw04", "hw05", "hw06", "hw07"):
        for cell in cells:
            text = "".join(cell["source"])
            if cell["cell_type"] == "markdown" and "## Required AI-use record" in text:
                cell["source"] = text.split("## Required AI-use record")[0].rstrip().splitlines(True)
                break
        records = {"hw04": HW4_AI_RECORD, "hw05": HW5_AI_RECORD, "hw06": HW6_AI_RECORD, "hw07": HW7_AI_RECORD}
        cells.append(markdown_cell(records[hw_id]))
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
