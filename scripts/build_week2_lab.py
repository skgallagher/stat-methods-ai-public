"""Build the clean Week 2 DynaSent lab and its instructor solution."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDENT_OUT = ROOT / "weeks" / "week02" / "lab.ipynb"
SOLUTION_OUT = ROOT / "instructor_only" / "week02" / "lab_solution.ipynb"

DATA_URL = (
    "https://raw.githubusercontent.com/skgallagher/stat-methods-ai-public/"
    "main/data/course/dynasent/items.csv"
)


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(True),
    }


def callout(title: str, body: str, *, color: str, background: str) -> dict:
    return markdown(
        f'''<div style="border-left: 6px solid {color}; background: {background};
padding: 0.9rem 1rem; margin: 1rem 0; border-radius: 0.35rem;">
<div style="font-weight: 800; letter-spacing: 0.04em; color: {color};
margin-bottom: 0.35rem;">{title}</div>
{body}
</div>
'''
    )


def your_turn(body: str) -> dict:
    return callout(
        "✍️ YOUR TURN", body, color="#8a5a00", background="#fff4c7"
    )


def context(body: str) -> dict:
    return callout(
        "🔎 CONTEXT", body, color="#155a8a", background="#e8f4ff"
    )


def response(prompt: str, answer: str | None) -> dict:
    prompt_html = (
        f'<p style="margin: 0 0 0.55rem 0;"><strong>{escape(prompt)}</strong></p>'
    )
    if answer is None:
        return your_turn(
            prompt_html + '<p style="margin: 0;"><em>Write your response here.</em></p>'
        )
    return callout(
        "✓ SAMPLE SOLUTION",
        prompt_html + f'<p style="margin: 0;">{escape(answer)}</p>',
        color="#1f6b45",
        background="#e9f7ef",
    )


def build(solution: bool) -> dict:
    answer = (lambda text: text) if solution else (lambda text: None)
    cells = [
        markdown(
            """# Lab 2: When a Label Is a Measurement

Sentiment labels can look like facts attached to sentences. DynaSent instead
records several people's judgments. Today we ask:

> **What changes when we treat a label as a measurement rather than truth?**

We use one dataset throughout. Each sentence has five judgments—`negative`,
`neutral`, or `positive`—plus a frozen model probability vector. The data load
directly from the course GitHub repository. No upload or local path is needed.
"""
        ),
        code(
            f'''import numpy as np
import pandas as pd
from sklearn.preprocessing import label_binarize

DATA_URL = {DATA_URL!r}
items = pd.read_csv(DATA_URL)

LABELS = ["negative", "neutral", "positive"]
VOTE_COLS = [f"{{label}}_votes" for label in LABELS]
MODEL_COLS = [f"model_p_{{label}}" for label in LABELS]

assert len(items) == 72
assert items[VOTE_COLS].sum(axis=1).eq(5).all()
assert np.allclose(items[MODEL_COLS].sum(axis=1), 1)

print(f"Loaded {{len(items)}} DynaSent sentences directly from GitHub.")
items[["item_id", "sentence", "collection_round"]].head(3)'''
        ),
        markdown(
            """## 1. Label six sentences yourself

Read these sentences before looking at the DynaSent judgments. For each one,
choose `negative`, `neutral`, or `positive`, and give a confidence from 0.50 to
1.00. You are recording your own judgment—not guessing the majority vote.
"""
        ),
        your_turn(
            """<p style="margin: 0;"><strong>Read the six sentences, then edit
<code>YOUR_LABELS</code> and <code>YOUR_CONFIDENCE</code> in the next code
cell.</strong> Do this before revealing the five DynaSent judgments.</p>"""
        ),
        code(
            '''# Choose two examples at each eventual agreement level, but hide the votes.
agreement_level = items[VOTE_COLS].max(axis=1)
label_items = (
    pd.concat([
        items.loc[agreement_level.eq(level)].sample(2, random_state=2027 + level)
        for level in [3, 4, 5]
    ])
    .sample(frac=1, random_state=2027)
    .reset_index(drop=True)
)

label_items[["item_id", "sentence"]]'''
        ),
        code(
            '''# During lab, replace these defaults before revealing the votes.
# Leaving them unchanged is safe when you are previewing or restarting the notebook.
# Example: YOUR_LABELS = ["neutral", "positive", ...]
YOUR_LABELS = ["not recorded"] * 6
YOUR_CONFIDENCE = [np.nan] * 6

my_judgments = label_items[["item_id", "sentence"]].copy()
my_judgments["my_label"] = YOUR_LABELS
my_judgments["my_confidence"] = YOUR_CONFIDENCE
my_judgments'''
            if not solution
            else '''# One possible set of judgments; these are not answer-key labels.
YOUR_LABELS = ["neutral", "negative", "positive", "neutral", "negative", "neutral"]
YOUR_CONFIDENCE = [0.70, 0.80, 0.65, 0.60, 0.75, 0.55]

my_judgments = label_items[["item_id", "sentence"]].copy()
my_judgments["my_label"] = YOUR_LABELS
my_judgments["my_confidence"] = YOUR_CONFIDENCE
my_judgments'''
        ),
        markdown("### Now reveal the five judgments\n"),
        code(
            '''revealed = my_judgments.merge(
    items[["item_id", *VOTE_COLS]], on="item_id", how="left"
)
revealed'''
        ),
        response(
            "Choose one sentence for which the five judgments capture something your single label does not.",
            answer(
                "For a sentence split 3–2 between neutral and positive, the vote counts preserve genuine hesitation between two plausible readings. My single label hides that division."
            ),
        ),
        markdown(
            """## 2. Build the item-level table

For each sentence we want the observed vote proportions, the majority label,
and an agreement pattern. With five judgments, the possible patterns are `5–0`,
`4–1`, and `3–2`.

Those are the only possibilities **because this teaching subset is restricted
to sentences receiving votes in no more than two sentiment categories**. A
split such as `3–1–1` cannot occur here. This is a selection rule for our subset,
not a general property of multiclass labels.

The class proportions are empirical measurements from these five judgments.
They are not being declared the population's true sentiment probabilities.
"""
        ),
        your_turn(
            """<ol style="margin: 0.2rem 0 0 1.2rem; padding: 0;">
<li>Calculate the summary for the first row by hand.</li>
<li>Trace the three numbered choices in the supplied code.</li>
<li>Run the structural checks.</li>
<li>Answer the highlighted interpretation questions.</li>
</ol>"""
        ),
        code(
            '''# Start with one row so the calculation is visible before it is automated.
items.loc[[0], ["sentence", *VOTE_COLS]]'''
        ),
        response(
            "For this row, report the three vote proportions, majority label, and agreement pattern.",
            answer(
                "The proportions are (0.8 negative, 0.2 neutral, 0 positive), the majority label is negative, and the agreement pattern is 4–1."
            ),
        ),
        code(
            ('''summary = items.copy()

# The 5–0 / 4–1 / 3–2 notation assumes at most two categories receive votes.
# Verify that deliberate subset restriction before constructing the pattern.
n_categories_used = summary[VOTE_COLS].gt(0).sum(axis=1)
assert n_categories_used.le(2).all()

# Choice 1: each sentence has five recorded judgments.
N_JUDGMENTS = 5
for label in LABELS:
    summary[f"q_{label}"] = summary[f"{label}_votes"] / N_JUDGMENTS

# Choice 2: remove the suffix from names such as "negative_votes".
VOTE_SUFFIX = "_votes"
largest_vote_column = summary[VOTE_COLS].idxmax(axis=1)
summary["majority_label"] = largest_vote_column.str.removesuffix(VOTE_SUFFIX)

# Choice 3: the two largest counts give a pattern such as "4–1".
def make_agreement_pattern(row):
    counts = sorted([row[column] for column in VOTE_COLS], reverse=True)
    return f"{counts[0]}–{counts[1]}"

summary["agreement_pattern"] = summary.apply(make_agreement_pattern, axis=1)

Q_COLS = [f"q_{label}" for label in LABELS]
assert np.allclose(summary[Q_COLS].sum(axis=1), 1)
assert set(summary["agreement_pattern"]) == {"5–0", "4–1", "3–2"}

summary[["sentence", *VOTE_COLS, *Q_COLS, "majority_label", "agreement_pattern"]].head()'''
            if not solution
            else '''summary = items.copy()

# The 5–0 / 4–1 / 3–2 notation assumes at most two categories receive votes.
n_categories_used = summary[VOTE_COLS].gt(0).sum(axis=1)
assert n_categories_used.le(2).all()

# 1. Divide each class count by the five judgments.
N_JUDGMENTS = 5
for label in LABELS:
    summary[f"q_{label}"] = summary[f"{label}_votes"] / N_JUDGMENTS

# 2. The largest count identifies the majority class; remove the column suffix.
VOTE_SUFFIX = "_votes"
largest_vote_column = summary[VOTE_COLS].idxmax(axis=1)
summary["majority_label"] = largest_vote_column.str.removesuffix(VOTE_SUFFIX)

# 3. The two largest counts form the agreement pattern.
def make_agreement_pattern(row):
    counts = sorted([row[column] for column in VOTE_COLS], reverse=True)
    return f"{counts[0]}–{counts[1]}"

summary["agreement_pattern"] = summary.apply(make_agreement_pattern, axis=1)

Q_COLS = [f"q_{label}" for label in LABELS]
assert np.allclose(summary[Q_COLS].sum(axis=1), 1)
assert set(summary["agreement_pattern"]) == {"5–0", "4–1", "3–2"}

summary[["sentence", *VOTE_COLS, *Q_COLS, "majority_label", "agreement_pattern"]].head()''')
        ),
        response(
            "Trace the supplied code: why do we divide by 5, remove `_votes`, and retain only the two largest counts?",
            answer(
                "We divide by 5 to turn counts into proportions, remove `_votes` to recover the class name, and retain the two largest counts because the teaching subset uses at most two categories per sentence."
            ),
        ),
        response(
            "What information is lost when five judgments become one majority label?",
            answer(
                "The majority label discards both the strength of agreement and the identity of the plausible alternative class. A 3–2 split and a 5–0 split become indistinguishable."
            ),
        ),
        markdown(
            """## 3. Compare random and high-disagreement sentences

The selection rules are explicit:

- **random:** three rows sampled with `random_state=2027`;
- **high disagreement:** three rows sampled from the `3–2` items with the same
  random state.

The displayed columns come from the `summary` table you built in Section 2:
the original sentence, its three vote counts, and its agreement pattern. The
code below selects and formats them for you.
"""
        ),
        your_turn(
            """<ol style="margin: 0.2rem 0 0 1.2rem; padding: 0;">
<li>Read all six complete sentences.</li>
<li>For each <code>3–2</code> item, identify the two labels that received votes.</li>
<li>Compare the wording in the random and high-disagreement sets.</li>
<li>Answer the highlighted interpretation question.</li>
</ol>"""
        ),
        code(
            '''# Supplied display code: no blanks to fill in this cell.
# These columns already exist in the Section 2 summary table.
example_columns = ["sentence", *VOTE_COLS, "agreement_pattern"]

random_examples = summary.sample(3, random_state=2027)
high_disagreement_examples = (
    summary.query("agreement_pattern == '3–2'")
    .sample(3, random_state=2027)
)

def show_sentence_examples(frame, caption):
    """Show complete, wrapped sentences alongside compact vote columns."""
    return (
        frame[example_columns]
        .style
        .hide(axis="index")
        .set_caption(caption)
        .set_properties(
            subset=["sentence"],
            **{
                "white-space": "pre-wrap",
                "text-align": "left",
                "min-width": "520px",
                "max-width": "700px",
            },
        )
        .set_properties(
            subset=VOTE_COLS + ["agreement_pattern"],
            **{"text-align": "center", "min-width": "85px"},
        )
        .set_table_styles([
            {"selector": "caption", "props": [
                ("caption-side", "top"),
                ("font-weight", "bold"),
                ("font-size", "1.05rem"),
                ("text-align", "left"),
            ]}
        ])
    )

display(show_sentence_examples(random_examples, "Randomly sampled items"))
display(show_sentence_examples(
    high_disagreement_examples,
    "High-disagreement items: five votes split 3–2",
))'''
        ),
        response(
            "Which two labels divide each 3–2 item? Name one recurring source of ambiguity, if one appears. Why should we avoid claiming that it explains every 3–2 item?",
            answer(
                "Several examples describe events without an explicit evaluation, so neutral and a valenced reading can both seem reasonable. Three examples cannot establish one universal mechanism for all disagreement."
            ),
        ),
        markdown(
            """## 4. How did the construction process change?

The word *round* refers to a round of **dataset construction**, not a second
rating of the same sentences. The five-person validation task was the same in
both rounds, but the sentences entering that task came from different processes.
"""
        ),
        context(
            """<table style="border-collapse: collapse; width: 100%;">
<thead><tr><th style="text-align:left; padding:0.35rem;">Round</th>
<th style="text-align:left; padding:0.35rem;">Where did its sentences come from?</th></tr></thead>
<tbody>
<tr><td style="padding:0.35rem; vertical-align:top;"><strong>1</strong></td>
<td style="padding:0.35rem;">Naturally occurring Yelp review sentences selected
because an initial sentiment model found them challenging.</td></tr>
<tr><td style="padding:0.35rem; vertical-align:top;"><strong>2</strong></td>
<td style="padding:0.35rem;">Crowdworkers edited Yelp prompts with the goal of
fooling a newer model trained using Round 1; the resulting sentences were then
validated by five raters.</td></tr>
</tbody></table>
<p style="margin:0.65rem 0 0 0;"><strong>Teaching-subset note:</strong> our
72 rows include 36 items from each round and use agreement-pattern quotas that
roughly mirror the eligible pools. This is a designed teaching subset, not a
simple random sample of all DynaSent sentences.</p>"""
        ),
        your_turn(
            """<p style="margin:0;"><strong>Run the next cell and compare the
within-round percentages.</strong> Then describe what the table shows and explain
why “raters became more certain in Round 2” goes beyond the evidence.</p>"""
        ),
        code(
            '''ROW_VARIABLE = "collection_round"
COLUMN_VARIABLE = "agreement_pattern"

round_counts = pd.crosstab(
    summary[ROW_VARIABLE], summary[COLUMN_VARIABLE]
)
round_percent = (
    pd.crosstab(
        summary[ROW_VARIABLE], summary[COLUMN_VARIABLE], normalize="index"
    )
    .mul(100)
    .round(1)
)

print("COUNTS")
display(round_counts)
print("WITHIN-ROUND PERCENTAGES")
display(round_percent)'''
        ),
        response(
            "What differs between the rounds in this teaching subset? Why is “raters became more certain in Round 2” too strong? Give one plausible alternative explanation.",
            answer(
                "Round 2 has a larger percentage of unanimous items in this teaching subset. This is agreement on different sentences, not repeated confidence measurements from the same raters; the different sentence-construction and selection processes could have produced a mix of items on which sentiment was easier to agree."
            ),
        ),
        markdown(
            r"""## 5. Score one forecast against two targets

Each row contains a frozen model probability vector

$$p=(p_{\mathrm{neg}},p_{\mathrm{neutral}},p_{\mathrm{positive}}).$$

We hold that forecast fixed and change the target:

- **hard target:** the one-hot encoding of the majority label;
- **soft target:** the three observed vote proportions.

In the class order negative, neutral, positive, write the target vector as

$$t=(t_1,t_2,t_3),$$

where $t_k$ is the target value for class $k$. For example, if the five votes
are $(4,1,0)$, then the majority label is negative. The hard target is

$$t_{\text{hard}}=(1,0,0),$$

while the soft target retains the vote proportions:

$$t_{\text{soft}}=(0.8,0.2,0).$$

For either choice of $t$, the unnormalized three-class Brier score is

$$B(p,t)=\sum_{k=1}^3(p_k-t_k)^2.$$

Scikit-learn's `label_binarize` creates the hard target. The standard
classification Brier scorer expects one observed class per row, so we apply the
four-line vector formula ourselves to support the empirical soft targets too.
"""
        ),
        code(
            '''model_probability = summary[MODEL_COLS].to_numpy()

# Hard target: one 1 and two 0s, based on the majority label.
hard_target = label_binarize(summary["majority_label"], classes=LABELS)

# Soft target: the observed proportions among five judgments.
soft_target = summary[Q_COLS].to_numpy()

def multiclass_brier(probability, target):
    """One unnormalized three-class Brier score per row."""
    squared_difference = np.square(probability - target)
    return squared_difference.sum(axis=1)

summary["hard_brier"] = multiclass_brier(model_probability, hard_target)
summary["soft_brier"] = multiclass_brier(model_probability, soft_target)

assert summary[["hard_brier", "soft_brier"]].ge(0).all().all()
assert summary[["hard_brier", "soft_brier"]].le(2).all().all()

summary[[
    "sentence", "majority_label", *Q_COLS, *MODEL_COLS,
    "hard_brier", "soft_brier"
]].head()'''
        ),
        code(
            '''# Inspect a sentence for which target construction matters substantially.
summary["score_difference"] = (
    summary["hard_brier"] - summary["soft_brier"]
).abs()

case = summary.nlargest(1, "score_difference")
case[[
    "sentence", *VOTE_COLS, *MODEL_COLS,
    "hard_brier", "soft_brier", "score_difference"
]]'''
        ),
        response(
            "Why do the two scores differ? Does a lower soft-target score prove that the soft target is always correct?",
            answer(
                "The forecast is unchanged, but the hard target erases minority judgments while the soft target retains them. A lower soft-target score only describes fit to that chosen empirical target; it does not establish that this target matches every scientific or decision goal."
            ),
        ),
        markdown(
            """## 6. What assumptions would justify averaging raters?

Before asking whether measurements are independent, name the random experiment.

- **Within one fixed sentence:** condition on $X=x$ and consider how raters were
  assigned and whether they worked separately.
- **Across random sentences:** draw one $X$, then give that same item to every
  rater or forecaster. The shared random item can make their responses move
  together.

Exchangeability is separate: would swapping the identities of two raters leave
the response model unchanged?
"""
        ),
        context(
            """<p style="margin:0 0 0.55rem 0;"><strong>Worked case: one expert
and four novices.</strong></p>
<p style="margin:0;">For a fixed sentence, independence is plausible if they
work separately. Exchangeability across all five is not plausible if expertise
changes response probabilities: swapping the expert with a novice changes the
model. The four novices might still be exchangeable with one another.</p>"""
        ),
        your_turn(
            """<p style="margin:0;"><strong>Complete every blank cell in the
table below.</strong> In the first row, reason conditional on a fixed sentence.
In the second, reason marginally over a randomly drawn sentence. Keep
independence and exchangeability separate.</p>"""
        ),
        markdown(
            """| Random experiment | Independence | Exchangeability |
|---|---|---|
| Fix one sentence; five crowd raters use one protocol and cannot see one another's answers |  |  |
| Draw one sentence $X$ at random; a student and two frozen classifiers forecast that same $X$ |  |  |
"""
            if not solution
            else """| Random experiment | Independence | Exchangeability |
|---|---|---|
| Fix one sentence; five crowd raters use one protocol and cannot see one another's answers | Conditional independence is plausible if assignment was separate and answers were hidden. We still need design evidence about communication, shared batches, and repeated workers. | Plausible if raters were sampled symmetrically from one pool and used the same instructions, training, and incentives. |
| Draw one sentence $X$ at random; a student and two frozen classifiers forecast that same $X$ | Independence is not justified merely because the forecasts were produced separately. All three are functions of the same random sentence, so item difficulty or ambiguity can induce marginal dependence. Conditional on fixed $X=x$, the model outputs are deterministic, so iid rater sampling is not the useful model. | Not plausible: the student and models have different information, training histories, objectives, and response mechanisms. |
"""
        ),
        response(
            "Even if an iid rater model is not justified, what do the observed vote proportions still describe?",
            answer(
                "They still describe the distribution of the five recorded judgments for that sentence under the actual labeling procedure."
            ),
        ),
        markdown("## Exit ticket\n"),
        response(
            "In one or two sentences, state what the empirical vote proportions measure and name one choice made when those measurements become a benchmark target.",
            answer(
                "The proportions measure how five recorded judgments were distributed across the three labels. Benchmark builders must still choose whether to retain that distribution or collapse it, for example by majority vote."
            ),
        ),
        markdown(
            """## Before leaving

- [ ] Your six judgments were recorded before the votes were revealed.
- [ ] The item-level checks pass.
- [ ] You inspected actual random and 3–2 sentences.
- [ ] Your round comparison shows denominators and avoids a causal claim.
- [ ] You can point to the exact code that creates both Brier-score columns.

**HW2 begins here:** it formalizes the distinction among an individual label,
an empirical vote distribution, a majority target, and a forecast.
"""
        ),
    ]

    for index, cell in enumerate(cells):
        cell["id"] = f"week02-{'solution' if solution else 'student'}-{index:03d}"
    return {
        "cells": cells,
        "metadata": {
            "colab": {
                "name": "week02_lab_solution.ipynb" if solution else "week02_lab.ipynb",
                "provenance": [],
            },
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    STUDENT_OUT.write_text(json.dumps(build(False), indent=1, ensure_ascii=False) + "\n")
    SOLUTION_OUT.write_text(json.dumps(build(True), indent=1, ensure_ascii=False) + "\n")
    print("wrote", STUDENT_OUT.relative_to(ROOT))
    print("wrote", SOLUTION_OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
