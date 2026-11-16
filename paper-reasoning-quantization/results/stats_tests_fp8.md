# Statistical tests (P-003b): Wilcoxon signed-rank + Holm, alpha=0.05

Units: (fixture, rep), judges averaged; Holm within each family.
"effect" = p_holm < alpha AND |Δ| > pooled 95th percentile of
within-config repeat spread (E-008 threshold).

## Family: quantization (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| NVFP4 vs FP8, T=0.0 thinking OFF | MQM | 21 | 18 | +11.29 | 45 | 0.0770 | 0.1540 | 17.45 | no |
| NVFP4 vs FP8, T=0.0 thinking ON | MQM | 21 | 13 | -0.71 | 45 | 0.9721 | 0.9721 | 32.35 | no |

## Family: temperature (4 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| T=0.0 vs T=0.2, FP8 thinking OFF (legacy engine) | MQM | 21 | 16 | -3.64 | 48 | 0.3004 | 0.6008 | 18.00 | no |
| T=0.8 vs T=0 anchor, FP8 thinking OFF | MQM | 21 | 17 | -0.74 | 60 | 0.4209 | 0.6008 | 44.40 | no |
| T=0.8 vs T=0 anchor, FP8 thinking ON | MQM | 21 | 17 | +15.05 | 29 | 0.0244 | 0.0733 | 35.37 | no |
| T=0.8 vs T=0.2, FP8 thinking ON (legacy engine) | MQM | 21 | 18 | +6.12 | 30 | 0.0155 | 0.0620 | 76.80 | no |

## Family: thinking (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 T=0.0 | MQM | 21 | 18 | -31.71 | 2 | 0.0003 | 0.0006 | 18.85 | YES |
| thinking ON vs OFF, FP8 T=0.8 | MQM | 21 | 19 | -15.93 | 18 | 0.0018 | 0.0018 | 60.70 | no |

## Family: defect/code_missing (4 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 T=0.0 | D3 code | 21 | 13 | +2.48 | 0 | 0.0011 | 0.0044 | 1.00 | YES |
| thinking ON vs OFF, FP8 T=0.8 | D3 code | 21 | 10 | +1.76 | 4 | 0.0129 | 0.0386 | 5.85 | no |
| T=0.8 vs T=0 anchor, FP8 thinking OFF | D3 code | 21 | 5 | +0.38 | 2 | 0.1308 | 0.2616 | 2.90 | no |
| T=0.8 vs T=0 anchor, FP8 thinking ON | D3 code | 21 | 5 | -0.33 | 4 | 0.3430 | 0.3430 | 7.00 | no |

## Family: defect/contam_nc (3 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 T=0.8 | D7nc contr | 21 | 2 | -0.05 | 1 | 0.6547 | 0.9519 | 1.00 | no |
| T=0.8 vs T=0 anchor, FP8 thinking OFF | D7nc contr | 21 | 1 | +0.10 | 0 | 0.3173 | 0.9519 | 0.00 | no |
| T=0.8 vs T=0 anchor, FP8 thinking ON | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 0.9519 | 0.00 | no |

## Family: defect/term_missing_nc (4 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 T=0.0 | D5nc term | 21 | 7 | -0.14 | 8 | 0.2568 | 0.7705 | 1.00 | no |
| thinking ON vs OFF, FP8 T=0.8 | D5nc term | 21 | 6 | +0.00 | 10 | 1.0000 | 1.0000 | 1.00 | no |
| T=0.8 vs T=0 anchor, FP8 thinking OFF | D5nc term | 21 | 8 | -0.05 | 16 | 0.7630 | 1.0000 | 1.00 | no |
| T=0.8 vs T=0 anchor, FP8 thinking ON | D5nc term | 21 | 2 | +0.10 | 0 | 0.1573 | 0.6292 | 1.00 | no |

## Noise floor (T=0, greedy; server non-determinism)

| cond | MQM p95 of |Δrep| | MQM sd (mixed) | D3 code | D4 num | D5nc term | D6 echo | D7nc contr (pure repeat sd) |
|---|---|---|---|---|---|---|---|
| FP8 T00 off | 16.00 | 3.95 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 |
| FP8 T00 on | 20.00 | 4.63 | 0.82 | 0.00 | 0.08 | 0.00 | 0.00 |

_MQM sd (mixed) here is sd over the 3 repeat means (judges averaged); the STATUS.md column 'noise' is sd over all 6 scores (3 reps × 2 judges)._
