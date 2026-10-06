# CFPB complaint-routing teaching extract

`complaints.csv` contains 400 public complaint narratives retrieved from the
Consumer Financial Protection Bureau Consumer Complaint Database API on
2026-09-01. The API and published data are CC0. Source and documentation:
<https://www.consumerfinance.gov/data-research/consumer-complaints/>.

## Frozen sampling design

The extract is deliberately stratified rather than prevalence-representative:

- calendar years 2022, 2023, 2024, and 2025;
- five product categories whose recorded names remain stable across those years;
- 20 complaints per product-by-year cell, for 400 rows total;
- candidate pools formed from the first and last 100 public narratives in each
  cell, followed by a deterministic hash draw; and
- one exact normalized duplicate pair retained when a candidate cell contains
  one, so grouped-split exercises use real repeated templates.

The five categories are checking or savings accounts, debt collection,
mortgages, student loans, and vehicle loans or leases. The balanced construction
does **not** preserve natural product prevalence, complaint volume, or the full
CFPB taxonomy. It supports category- and time-aware teaching comparisons, not a
population estimate of the CFPB complaint stream.

`period` labels 2022–2023 as `source` and 2024–2025 as `target`; it is a teaching
partition, not an assertion that the underlying complaint process changed at a
single known boundary. `similarity_group` hashes exact normalized narrative
text, and `duplicate_flag` marks every row in a repeated group.

All public narratives in this extract were submitted through the Web channel.
This is a collection-process fact: the CFPB currently reports public narratives
only for Web submissions. Students should not infer that all CFPB complaints
arrive through the Web.

The CFPB states that narratives are consumers' descriptions, are published only
when consumers opt to share them after personal-information removal, and are
not a statistical sample of consumers' marketplace experiences. The Bureau
does not verify every allegation in a narrative.

Rebuild with `scripts/freeze_week3_cfpb.py`. Historical records in the live API
can change, so the checked-in CSV and `release_summary.json` are the frozen
course release.
