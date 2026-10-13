# Week 5 LLM comparison data: BIG-Bench Hard

Whether each of eight open-weight chat models got each **BIG-Bench Hard (BBH)**
question right, in the Open LLM Leaderboard v2 evaluation. All eight models
answered the same 5,761 multiple-choice questions in 24 tasks, so any two models
can be compared question by question.

## Files

- `correct.csv`: one row per question. `question_id`, `task`, then one column
  per model with 1 if that model got the question right and 0 if not.
- `questions.csv`: the question text (`input`), the right answer (`target`), and
  the number of answer options (`n_options`) for each `question_id`.
- `models.csv`: one row per model. `column` is the model's column name in
  `correct.csv`. `parameters_billion` is the safetensors parameter total on the
  model's Hugging Face page; `memory_gb_16bit` is 2 bytes per parameter, the
  memory for the weights alone at 16-bit precision. `license` is the model's
  license as listed on its Hugging Face page in October 2026.
- `release_summary.json`: frozen counts, accuracies, and source hashes.

## Source

The per-question results are from the Open LLM Leaderboard's "details" datasets
on Hugging Face (`open-llm-leaderboard/<model>-details`, listed in `models.csv`),
which record every question, the model's score for each answer option, and
whether the model was right. The leaderboard ran the models with EleutherAI's
`lm-evaluation-harness`, three worked examples before each question, and each
model's chat format. The run dates differ by model and are in `models.csv`.

The questions are from Suzgun et al. (2022), "Challenging BIG-Bench Tasks and
Whether Chain-of-Thought Can Solve Them," released under the MIT License, which
draws its tasks from BIG-bench (Apache 2.0). The details datasets are gated
with automatic approval, and their dataset cards do not state a license. This
release redistributes the BBH questions and the derived right/wrong outcomes,
not the models' option scores or prompts.

## What "right" means

The model does not write out an answer. For each answer option, the harness
computes the model's log-probability of that option's text, divided by the
option's length, and the model's answer is the option with the highest value.
This is the leaderboard's `acc_norm`. A model that would answer correctly in
free text can still be scored wrong, and the reverse.

The accuracies here are the share of all 5,761 questions answered right. The
leaderboard's displayed BBH score is computed differently: it subtracts the
random-guessing rate in each task and averages over tasks, so its numbers do not
match these.

## Limitations

- The 24 tasks are a fixed, published benchmark, not a random sample of
  reasoning problems. Task sizes differ (146 to 250 questions).
- BBH questions have been public since 2022 and may appear in some models'
  training data. Good scores can partly reflect memorized questions.
- Each model was scored once, with one prompt format. Different prompts or
  scoring rules can change the accuracies and the ranking.
- Do not use `questions.csv` to train or tune a model.

Rebuild with `scripts/freeze_week5_llm.py`. The source datasets can change, so
the checked-in files and `release_summary.json` are the frozen course release.
