# Week 2 CFPB teaching extract

`complaints.csv` contains 100 public complaint narratives retrieved from the
Consumer Financial Protection Bureau Consumer Complaint Database API. The API
and published data are CC0. Source and documentation:
<https://www.consumerfinance.gov/data-research/consumer-complaints/>.

The frozen query requested complaints received during 2024–2025 having a public
narrative, sorted by received date. The extract retains the first 100 returned
records and adds exact-normalized-text grouping and duplicate indicators.

All public narratives in this extract were submitted through the Web channel.
This is itself a collection-process fact: the CFPB currently reports public
narratives only for Web submissions. Students should not infer that all CFPB
complaints arrive through the Web.

The CFPB states that complaint narratives are consumers’ descriptions, are
published only when consumers opt to share them after personal-information
removal, and are not a statistical sample of consumers’ marketplace experiences.
