# Week 2 practice — labels, targets, and adaptive collection

Complete without AI. Suggested time: 18 minutes. This is a parallel practice
problem, not a homework answer key.

## Scenario

A sentiment item receives five labels: one negative, one neutral, and three
positive. A model assigns probabilities $(0.20,0.30,0.50)$ to negative, neutral,
and positive.

1. Write the one-hot majority target and the rater-proportion target. Compute the
   unnormalized multiclass Brier score against each target. In one sentence,
   explain why the two scores answer different questions.

2. A benchmark contains the following item-level results:

   | Collection | Vote pattern | Items | Model correct |
   |---|---|---:|---:|
   | Natural Round 1 | 5–0 or 4–1 | 80 | 68 |
   | Natural Round 1 | 3–2 | 20 | 12 |
   | Model-in-the-loop Round 2 | 5–0 or 4–1 | 40 | 30 |
   | Model-in-the-loop Round 2 | 3–2 | 60 | 24 |

   Compute accuracy within each row and overall within each round. Give one
   compositional explanation for the overall round difference and one additional
   plausible explanation. Why is neither a causal effect estimate?

3. An analyst deletes all 3–2 items and writes, “Cleaning noisy labels proves the
   model works on sentiment.” Name the resulting analysis population and rewrite
   the claim so it matches the evidence.

4. Classify each design as plausibly independent, plausibly exchangeable, both,
   or neither. Justify each answer briefly.

   a. An expert and a novice label separately, but their response probabilities
   differ.

   b. Five raters are sampled symmetrically. Before they begin, one unrecorded
   strict-versus-lenient instruction variant is selected and shown to all five.
   Conditional on that shared variant, they work independently.

   c. Draw one sentence $X$ at random. Two raters work independently conditional
   on $X=x$, but both are more likely to choose positive on clearly positive
   sentences than on ambiguous or negative sentences. Are their labels
   necessarily independent marginally over random $X$?
