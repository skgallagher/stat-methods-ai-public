# Week 9 lab data: Camelyon17 tissue patches

Small patches of lymph-node tissue slides from five hospitals in the Netherlands, each
labeled by pathologists as containing tumor or not, with a model's predicted probability
of tumor. Built by `scripts/freeze_week9_camelyon.py`.

## Files

- `patches.npz`: one array, `images`, of shape (patches, 96, 96, 3), uint8 RGB. Row *i*
  is the patch in row *i* of `patches.csv`.
- `patches.csv`: `patch_id`; `group` (`benchmark`, `hospital 4`, or `hospital 5`);
  `hospital` (1 to 5); `slide_id` (patches from one slide share it); `label` (1 if the
  center of the patch contains tumor); `p_tumor` (the model's probability of tumor);
  `predicted_tumor` (1 if `p_tumor` is at least 0.5).
- `release_summary.json`: counts, accuracies, the pinned source revision, and the seed.

## The model

ImageNet ResNet-18 features followed by logistic regression, fitted on other slides from
hospitals 1, 2, and 3. Those fitting patches are not included. The `benchmark` patches come
from held-out slides of hospitals 1 to 3; hospitals 4 and 5 were never seen by the model.

## Sampling

This is a small teaching subset, not a probability sample. Hospitals 4 and 5 each have
150 tumor and 150 non-tumor patches. The benchmark is about 55% tumor overall, but its
hospitals differ: about 78% tumor at hospital 1, 63% at hospital 2, and 24% at hospital 3.
Either way, the share of tumor patches does not match a real slide, where most tissue is
not tumor. Patches from one slide are related, so resample slides, not patches, for
intervals.

## Source and license

Camelyon17-WILDS (Koh et al. 2021, "WILDS: A Benchmark of in-the-Wild Distribution
Shifts"), built from the CAMELYON17 challenge (Bandi et al. 2019). WILDS lists the dataset
as public domain under CC0. Downloaded from the Hugging Face mirror
`wltjr1007/Camelyon17-WILDS` at a pinned revision (see `release_summary.json`).
