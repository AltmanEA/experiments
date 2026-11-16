# Statistical tests (P-003b): Wilcoxon signed-rank + Holm, alpha=0.05

Units: (fixture, rep), judges averaged; Holm within each family.
"effect" = p_holm < alpha AND |Δ| > pooled 95th percentile of
within-config repeat spread (E-008 threshold).

## Family: placement-quantization (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| bf16 vs FP8, cloud thinking OFF (quantization) | MQM | 21 | 16 | +2.57 | 59 | 0.6413 | 1.0000 | 27.32 | no |
| local vs cloud FP8, thinking OFF (placement) | MQM | 21 | 18 | -0.52 | 84 | 0.9653 | 1.0000 | 23.77 | no |

## Family: defect/code_missing (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| bf16 vs FP8, cloud thinking OFF (quantization) | D3 code | 21 | 3 | -0.19 | 1 | 0.2850 | 0.2850 | 1.00 | no |
| local vs cloud FP8, thinking OFF (placement) | D3 code | 21 | 5 | +0.24 | 2 | 0.1290 | 0.2580 | 2.00 | no |

## Family: defect/contam_nc (1 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| local vs cloud FP8, thinking OFF (placement) | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 0.3173 | 0.00 | no |

## Family: defect/term_missing_nc (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| bf16 vs FP8, cloud thinking OFF (quantization) | D5nc term | 21 | 3 | -0.05 | 2 | 0.5637 | 1.0000 | 1.00 | no |
| local vs cloud FP8, thinking OFF (placement) | D5nc term | 21 | 3 | +0.05 | 2 | 0.5637 | 1.0000 | 1.00 | no |

## Noise floor (T=0, greedy; server non-determinism)

| cond | MQM p95 of |Δrep| | MQM sd (mixed) | D3 code | D4 num | D5nc term | D6 echo | D7nc contr (pure repeat sd) |
|---|---|---|---|---|---|---|---|
| P8 cloud FP8 (T=0.2) | 54.50 | 8.44 | 0.22 | 0.00 | 0.08 | 0.00 | 0.00 |

_MQM sd (mixed) here is sd over the 3 repeat means (judges averaged); the STATUS.md column 'noise' is sd over all 6 scores (3 reps × 2 judges)._
