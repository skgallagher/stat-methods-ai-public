"""HW4 Problem 3: an AI's attempted sequence bootstrap and the supplied checks.

The same code appears in hw04_starter.ipynb.
"""

import pandas as pd


def ai_bootstrap_attempt(data, seed=401):
    """Supposed to return the sequence IDs chosen in one sequence-bootstrap draw."""
    sampled_frames = data.sample(n=len(data), replace=True, random_state=seed)
    return list(sampled_frames["sequence_id"])


def supplied_checks(candidate, data):
    """Tests that any correct one-draw sequence bootstrap should pass."""
    n_sequences = data["sequence_id"].nunique()
    valid_ids = list(data["sequence_id"].unique())

    # Check 1: the number of draws.
    draws = candidate(data, seed=401)
    assert len(draws) == n_sequences, f"Expected {n_sequences} draws, got {len(draws)}."

    # Check 2: what each draw is.
    for sequence_id in draws:
        assert sequence_id in valid_ids, "Return sequence IDs."

    # Check 3: add a copy of one row and draw again.
    data_plus_copy = pd.concat([data, data.head(1)])
    draws_again = candidate(data_plus_copy, seed=401)
    assert len(draws_again) == n_sequences, f"After adding one row: expected {n_sequences} draws, got {len(draws_again)}."
