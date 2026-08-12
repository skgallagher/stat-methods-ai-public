# Week 2 DynaSent teaching extracts

These files are frozen subsets of DynaSent v1.1, described by Potts et al.
(2021), “DynaSent: A Dynamic Benchmark for Sentiment Analysis.” DynaSent is
distributed under CC BY 4.0. Source: <https://github.com/cgpotts/dynasent>.

- `items.csv`: 72 lab items, 36 from each construction round.
- `homework_items.csv`: 72 disjoint homework items, 36 from each round.
- `forecaster_items.csv`: 10 additional, purposefully selected forecast cases.

Each lab/homework row contains the sentence, five non-mixed judgment counts,
and the probability report from the pinned
`cardiffnlp/twitter-roberta-base-sentiment-latest` checkpoint at revision
`3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7`.

The lab and homework extracts are further restricted to items whose five votes
occupy no more than two of the three sentiment categories. Consequently their
agreement patterns can be summarized as `5–0`, `4–1`, or `3–2`. This restriction
is specific to these teaching extracts; DynaSent and multiclass labeling data in
general can contain votes spread across all three categories.

The lab and homework samples are deterministic teaching extracts, not
probability samples from a target population. Each contains 36 items per round
and uses agreement-pattern quotas that roughly track the eligible pools while
ensuring that `5–0`, `4–1`, and `3–2` all appear. The forecaster cases were
chosen to produce useful model disagreement and must not be used to estimate an
unselected benchmark-wide rate.
