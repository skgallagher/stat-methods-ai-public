# Week 12 data: human and GPT-4 judgments of chatbot answers (MT-Bench)

Six chat models answered 80 two-turn questions. For each pair of models, question, and
turn, expert humans voted on which answer was better, and GPT-4 gave a verdict too. Built
by `scripts/freeze_week12_mtbench.py`.

## Files

- `items.csv`: one row per item, 2,400 in all (80 questions × 2 turns × 15 pairs of
  models). `item_id`; `question_id` (81 to 160); `category`; `half` (`lab` for writing,
  roleplay, reasoning, and STEM; `homework` for math, coding, extraction, and humanities);
  `turn` (1 or 2); `model_1` and `model_2` (the two models, in alphabetical order);
  `gpt4_verdict` (`model_1`, `model_2`, or `tie`); `gpt4_orders_agree` (False when GPT-4's
  verdicts in the two answer orders disagreed); `n_human_votes`.
- `human_votes.csv`: one row per human vote, 3,354 in all. `item_id`; `judge` (an
  anonymous ID from the source, such as `expert_17`); `vote` (`model_1`, `model_2`, or
  `tie`).
- `questions.csv`: `question_id`, `category`, `turn_1`, `turn_2` (the user's two messages).
- `answers.csv`: `question_id`, `model`, `turn`, `answer` (each model's reply to each turn).
- `release_summary.json`: sources, pinned revisions, and counts.

## How the judgments were made

The human judges were mostly graduate students with expertise in each question's topic.
They saw a question and two models' answers and picked the better one or called a tie;
for a turn-2 item they judged the second reply. Many items have one human vote; 960 have
two or more. GPT-4 judged every item with FastChat's pairwise prompt at temperature 0,
twice, with the two answers in swapped positions. When the two orders gave the same
verdict, that is `gpt4_verdict`. When they differed, the source records a tie, and
`gpt4_orders_agree` is False (380 items). The file does not say which way each of those
verdicts went, so it shows how often the order changed the verdict, not which position
GPT-4 favored.

## What the data can and cannot say

The 80 questions were written by the MT-Bench authors, ten per category, so they are not
a random sample of what people ask chatbots. Items from the same question share its
difficulty and its answers, so intervals should resample questions. The human votes are
an imperfect reference: they agree with one another only about two-thirds of the time.
One judge voted twice on one item; the second vote was dropped. One answer is empty (LLaMA-13B on question 127, turn 1); read the file with `keep_default_na=False` so it stays an empty string.

## Source and license

`lmsys/mt_bench_human_judgments` on Hugging Face (Zheng et al. 2023, "Judging
LLM-as-a-Judge with MT-Bench and Chatbot Arena"), CC-BY-4.0, read from its Parquet
conversion at a pinned revision (see `release_summary.json`). The answers are outputs of
GPT-4, GPT-3.5-turbo, Claude-v1, Vicuna-13B, Alpaca-13B, and LLaMA-13B, each under its
provider's terms.
