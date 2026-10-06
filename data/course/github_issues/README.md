# Scikit-learn issue-triage teaching extract

This frozen Week 3 extract contains 120 real, closed issues from the public
[`scikit-learn/scikit-learn`](https://github.com/scikit-learn/scikit-learn/issues)
issue tracker. It was collected through the GitHub API on 2026-08-12.

## Selection

- Creation dates: 2018-01-01 through 2025-12-31.
- Eight real scikit-learn `module:*` labels.
- Fifteen issues per module, spaced through the eligible time-ordered records.
- Each selected issue had exactly one `module:*` label at the snapshot.
- Pull requests are excluded.

The extract is deliberately balanced by module. It is **not** a random sample
of the issue stream and does not preserve natural module prevalences. Excluding
multi-module issues also excludes a potentially harder part of real triage.

## Fields

- `issue_number`: public scikit-learn issue number.
- `title`: public issue title at the snapshot.
- `created_date`, `created_year`: issue creation date.
- `module_label`: final recorded `module:*` label at the snapshot.
- `reporter_group`: deterministic pseudonym for the public GitHub reporter;
  useful for grouped evaluation without distributing usernames.
- `source_url`: link to the original public issue for provenance and checking.

Only short titles and public metadata are redistributed. Issue bodies, comments,
and GitHub usernames are not included. Individual issue authors retain whatever
rights they hold in their contributions; the scikit-learn software's BSD license
should not be assumed to license every issue-tracker contribution. Keep source
links with any derived teaching subset.

## Statistical cautions

The recorded final module label is a maintainer decision, not independently
verified ground truth. Labels can be added or revised after discussion, and an
issue may reasonably touch multiple modules. The snapshot also cannot reveal
what information the triager used when assigning the label.

Rebuild deterministically with `scripts/build_week3_github_issues.py`; GitHub's
mutable issue history means a later rebuild may differ from this frozen release.
