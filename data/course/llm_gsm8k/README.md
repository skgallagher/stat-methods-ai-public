# Week 11 lab data: sampled answers to GSM8K math word problems

Two language models each answered 127 grade-school math word problems 10,000 times. Each
answer is marked right or wrong. Built by `scripts/freeze_week11_gsm8k.py`.

## Files

- `problems.csv`: one row per problem. `problem_id` (g001 to g127); `gsm8k_test_index`
  (the problem's row in GSM8K's test set); `question`; `answer` (the key's final number);
  `solution` (the key's worked solution); `right_8b` and `right_70b` (how many of each
  model's 10,000 answers are right); `most_common_wrong_8b` and
  `most_common_wrong_count_8b` (the 8B model's most common wrong final number, and how
  often it gave it); `no_final_answer_8b` (8B answers with no final number, which count as
  wrong).
- `correct.npz`: two arrays, `llama3_8b` and `llama3_70b`, each 127 by 10,000, True where
  the answer is right. Row *i* is row *i* of `problems.csv`. Column *j* is the model's
  *j*-th answer to that problem. Within one problem, accuracy is the same across the
  10,000 columns. Across problems, though, column *j* is not independent of itself: the
  *j*-th answers to all 127 problems rise and fall together, and the same columns run low
  for both models, which points to something shared by each column, most likely its
  random seed. A column's accuracy over the 127 problems has SD 0.039 for the 8B model,
  against 0.027 if every answer were independent. To act out fresh answers, draw a
  separate random column for each problem, as Lab 11 does.
- `answer_texts.csv`: the first right and the first wrong 8B answer to each problem, with
  `answer_index` (its column in `correct.npz`), `correct`, `final_answer`, and `text`.
  Two problems have no wrong answer among their 10,000, so they appear once.
- `prompts.csv`: the full prompt for each problem: five worked GSM8K examples, which are
  different for each problem, then the question.
- `release_summary.json`: sources, pinned revisions, sampling settings, and accuracies.

## How the answers were made

The models are Llama 3 8B Instruct and Llama 3 70B Instruct. Each answer was sampled at
temperature 0.6 with at most 512 new tokens, after a prompt of five worked examples. An
answer is right if the number after "####" matches the key's. An answer that runs out of
tokens before giving a number counts as wrong (378 of the 8B model's answers to g001, for
example). The 127 problems were drawn at random from GSM8K's 1,319 test problems; one
drawn problem with a wrong key was dropped by the dataset's authors.

## What the data can and cannot say

Each problem's 10,000 answers pin down how often one sampled answer to it is right, to
within about a point. The 127 problems are a random sample of GSM8K's test set, not of any
client's problems, so the average over problems describes GSM8K, and the problems
themselves are a sample: a new set of 127 would give a different average. Because the
worked examples differ by problem, part of what looks like a difference between problems
may come from their prompts.

## Source and license

`ScalingIntelligence/monkey_business` on Hugging Face (Brown et al. 2024, "Large Language
Monkeys: Scaling Inference Compute with Repeated Sampling"), MIT license, read from its
Parquet conversion at a pinned revision (see `release_summary.json`). GSM8K (Cobbe et al.
2021) is MIT-licensed. The answers are outputs of Meta's Llama 3 models, released under
the Meta Llama 3 Community License.
