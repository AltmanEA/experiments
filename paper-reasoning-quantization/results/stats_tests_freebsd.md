# Statistical tests (P-003b): Wilcoxon signed-rank + Holm, alpha=0.05

Units: (fixture, rep), judges averaged; Holm within each family.
"effect" = p_holm < alpha AND |Δ| > pooled 95th percentile of
within-config repeat spread (E-008 threshold).

## Family: temperature (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| T=0.0 vs T=0.2, thinking OFF (FreeBSD) | MQM | 15 | 11 | -0.77 | 22 | 0.3503 | 0.7006 | 26.30 | no |
| T=0.0 vs T=0.2, thinking ON (FreeBSD) | MQM | 15 | 12 | -0.27 | 38 | 0.9062 | 0.9062 | 15.55 | no |

## Family: thinking (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, NVFP4 T=0.0 (FreeBSD) | MQM | 15 | 12 | +7.80 | 6 | 0.0096 | 0.0187 | 16.55 | no |
| thinking ON vs OFF, NVFP4 T=0.2 (FreeBSD) | MQM | 15 | 10 | +7.30 | 2 | 0.0093 | 0.0187 | 23.55 | no |

## Family: defect/contam_nc (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, NVFP4 T=0.2 (FreeBSD) | D7nc contr | 15 | 1 | +0.07 | 0 | 0.3173 | 0.6346 | 0.55 | no |
| T=0.0 vs T=0.2, thinking ON (FreeBSD) | D7nc contr | 15 | 1 | -0.07 | 0 | 0.3173 | 0.6346 | 0.55 | no |

## Family: defect/term_missing_nc (3 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, NVFP4 T=0.0 (FreeBSD) | D5nc term | 15 | 3 | -0.20 | 0 | 0.0833 | 0.2498 | 0.00 | no |
| thinking ON vs OFF, NVFP4 T=0.2 (FreeBSD) | D5nc term | 15 | 1 | -0.07 | 0 | 0.3173 | 0.3173 | 0.55 | no |
| T=0.0 vs T=0.2, thinking ON (FreeBSD) | D5nc term | 15 | 2 | -0.13 | 0 | 0.1573 | 0.3146 | 0.55 | no |

## Noise floor (T=0, greedy; server non-determinism)

| cond | MQM p95 of |Δrep| | MQM sd (mixed) | D3 code | D4 num | D5nc term | D6 echo | D7nc contr (pure repeat sd) |
|---|---|---|---|---|---|---|---|
| F T00 off | 20.60 | 6.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| F T00 on | 15.30 | 4.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

_MQM sd (mixed) here is sd over the 3 repeat means (judges averaged); the STATUS.md column 'noise' is sd over all 6 scores (3 reps × 2 judges)._
