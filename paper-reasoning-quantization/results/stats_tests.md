# Statistical tests (P-003b): Wilcoxon signed-rank + Holm, alpha=0.05

Units: (fixture, rep), judges averaged; Holm within each family.
"effect" = p_holm < alpha AND |Δ| > pooled 95th percentile of
within-config repeat spread (E-008 threshold).

## Family: other (3 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| no glossary vs glossary, cloud | MQM | 21 | 19 | -8.19 | 63 | 0.1975 | 0.1975 | 27.12 | no |
| post-processing (clean vs raw) | MQM | 21 | 21 | -23.62 | 37 | 0.0064 | 0.0127 | 59.97 | no |
| thinking ON (clean) vs OFF, cloud | MQM | 21 | 21 | -56.50 | 0 | <0.0001 | 0.0002 | 53.15 | YES |

## Family: quantization (3 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| FP8 vs cloud bf16, thinking OFF | MQM | 21 | 17 | -3.10 | 52 | 0.2362 | 0.7087 | 19.00 | no |
| NVFP4 vs FP8, thinking OFF | MQM | 21 | 18 | -3.74 | 61 | 0.2854 | 0.7087 | 27.67 | no |
| NVFP4 vs FP8, thinking ON | MQM | 21 | 17 | -3.81 | 71 | 0.7946 | 0.7946 | 63.02 | no |

## Family: temperature (10 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| T=0.2 vs T=0 anchor, thinking OFF | MQM | 21 | 15 | -11.38 | 10 | 0.0045 | 0.0403 | 27.67 | no |
| T=0.2 vs T=0 anchor, thinking ON | MQM | 21 | 17 | +5.83 | 62 | 0.4925 | 0.7590 | 40.95 | no |
| T=0.4 vs T=0 anchor, thinking OFF | MQM | 21 | 17 | -3.79 | 58 | 0.3795 | 0.7590 | 36.57 | no |
| T=0.4 vs T=0 anchor, thinking ON | MQM | 21 | 17 | +13.71 | 26 | 0.0179 | 0.1073 | 41.00 | no |
| T=0.6 vs T=0 anchor, thinking OFF | MQM | 21 | 18 | -7.71 | 46 | 0.0893 | 0.2678 | 35.10 | no |
| T=0.6 vs T=0 anchor, thinking ON | MQM | 21 | 14 | +16.50 | 12 | 0.0100 | 0.0764 | 68.00 | no |
| T=0.8 vs T=0 anchor, thinking OFF | MQM | 21 | 17 | -7.86 | 30 | 0.0276 | 0.1104 | 19.47 | no |
| T=0.8 vs T=0 anchor, thinking ON | MQM | 21 | 16 | +24.60 | 23 | 0.0199 | 0.1073 | 81.60 | no |
| T=1.0 vs T=0 anchor, thinking OFF | MQM | 21 | 17 | -14.33 | 12 | 0.0024 | 0.0243 | 25.50 | no |
| T=1.0 vs T=0 anchor, thinking ON | MQM | 21 | 18 | +23.00 | 26 | 0.0096 | 0.0764 | 38.85 | no |

## Family: thinking (7 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 | MQM | 21 | 18 | -26.43 | 2 | 0.0003 | 0.0019 | 28.75 | no |
| thinking ON vs OFF, NVFP4 T=0.0 | MQM | 21 | 19 | -43.71 | 5 | 0.0003 | 0.0019 | 20.00 | YES |
| thinking ON vs OFF, NVFP4 T=0.2 | MQM | 21 | 17 | -26.50 | 10 | 0.0016 | 0.0082 | 40.95 | no |
| thinking ON vs OFF, NVFP4 T=0.4 | MQM | 21 | 20 | -26.21 | 22 | 0.0018 | 0.0082 | 60.67 | no |
| thinking ON vs OFF, NVFP4 T=0.6 | MQM | 21 | 18 | -19.50 | 22 | 0.0061 | 0.0182 | 71.80 | no |
| thinking ON vs OFF, NVFP4 T=0.8 | MQM | 21 | 19 | -11.26 | 50 | 0.0732 | 0.1464 | 81.60 | no |
| thinking ON vs OFF, NVFP4 T=1.0 | MQM | 21 | 17 | -6.38 | 61 | 0.4631 | 0.4631 | 38.60 | no |

## Family: defect/code_missing (23 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 | D3 code | 21 | 10 | +1.43 | 0 | 0.0036 | 0.0721 | 2.00 | no |
| thinking ON vs OFF, NVFP4 T=0.0 | D3 code | 21 | 15 | +2.71 | 0 | 0.0005 | 0.0109 | 1.00 | YES |
| thinking ON vs OFF, NVFP4 T=0.2 | D3 code | 21 | 8 | +1.29 | 0 | 0.0107 | 0.1821 | 2.00 | no |
| thinking ON vs OFF, NVFP4 T=0.4 | D3 code | 21 | 7 | +1.48 | 0 | 0.0167 | 0.2680 | 3.95 | no |
| thinking ON vs OFF, NVFP4 T=0.6 | D3 code | 21 | 11 | +1.52 | 0 | 0.0030 | 0.0633 | 6.00 | no |
| thinking ON vs OFF, NVFP4 T=0.8 | D3 code | 21 | 10 | +1.71 | 6 | 0.0264 | 0.3694 | 6.90 | no |
| thinking ON vs OFF, NVFP4 T=1.0 | D3 code | 21 | 7 | +2.24 | 0 | 0.0178 | 0.2680 | 8.85 | no |
| FP8 vs cloud bf16, thinking OFF | D3 code | 21 | 5 | +0.43 | 0 | 0.0394 | 0.4330 | 1.00 | no |
| NVFP4 vs FP8, thinking OFF | D3 code | 21 | 3 | -0.19 | 0 | 0.1025 | 0.8198 | 1.00 | no |
| NVFP4 vs FP8, thinking ON | D3 code | 21 | 11 | -0.33 | 22 | 0.2850 | 0.8198 | 3.00 | no |
| T=0.2 vs T=0 anchor, thinking OFF | D3 code | 21 | 3 | +0.29 | 0 | 0.0833 | 0.7494 | 0.00 | no |
| T=0.2 vs T=0 anchor, thinking ON | D3 code | 21 | 12 | -1.14 | 4 | 0.0051 | 0.0973 | 2.00 | no |
| T=0.4 vs T=0 anchor, thinking OFF | D3 code | 21 | 2 | +0.33 | 0 | 0.1797 | 0.8198 | 0.95 | no |
| T=0.4 vs T=0 anchor, thinking ON | D3 code | 21 | 13 | -0.90 | 16 | 0.0322 | 0.3987 | 2.00 | no |
| T=0.6 vs T=0 anchor, thinking OFF | D3 code | 21 | 3 | +0.24 | 0 | 0.1025 | 0.8198 | 0.00 | no |
| T=0.6 vs T=0 anchor, thinking ON | D3 code | 21 | 11 | -0.95 | 13 | 0.0672 | 0.6717 | 6.00 | no |
| T=0.8 vs T=0 anchor, thinking OFF | D3 code | 21 | 3 | +0.19 | 0 | 0.1025 | 0.8198 | 1.00 | no |
| T=0.8 vs T=0 anchor, thinking ON | D3 code | 21 | 11 | -0.81 | 16 | 0.1151 | 0.8198 | 6.90 | no |
| T=1.0 vs T=0 anchor, thinking OFF | D3 code | 21 | 3 | +0.19 | 0 | 0.1025 | 0.8198 | 1.00 | no |
| T=1.0 vs T=0 anchor, thinking ON | D3 code | 21 | 14 | -0.29 | 20 | 0.0307 | 0.3987 | 8.85 | no |
| no glossary vs glossary, cloud | D3 code | 21 | 1 | -0.05 | 0 | 0.3173 | 0.8198 | 0.00 | no |
| post-processing (clean vs raw) | D3 code | 21 | 9 | +0.76 | 0 | 0.0066 | 0.1189 | 7.00 | no |
| thinking ON (clean) vs OFF, cloud | D3 code | 21 | 12 | +3.43 | 0 | 0.0020 | 0.0447 | 2.00 | YES |

## Family: defect/contam_nc (15 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 | D7nc contr | 21 | 1 | -0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| thinking ON vs OFF, NVFP4 T=0.4 | D7nc contr | 21 | 1 | -0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| thinking ON vs OFF, NVFP4 T=0.6 | D7nc contr | 21 | 2 | -0.10 | 0 | 0.1573 | 1.0000 | 0.00 | no |
| thinking ON vs OFF, NVFP4 T=0.8 | D7nc contr | 21 | 1 | -0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| thinking ON vs OFF, NVFP4 T=1.0 | D7nc contr | 21 | 3 | -0.05 | 2 | 0.5637 | 1.0000 | 1.00 | no |
| FP8 vs cloud bf16, thinking OFF | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| NVFP4 vs FP8, thinking OFF | D7nc contr | 21 | 1 | -0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| T=0.4 vs T=0 anchor, thinking OFF | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| T=0.6 vs T=0 anchor, thinking OFF | D7nc contr | 21 | 2 | +0.10 | 0 | 0.1573 | 1.0000 | 0.00 | no |
| T=0.8 vs T=0 anchor, thinking OFF | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| T=1.0 vs T=0 anchor, thinking OFF | D7nc contr | 21 | 2 | +0.10 | 0 | 0.1573 | 1.0000 | 1.00 | no |
| T=1.0 vs T=0 anchor, thinking ON | D7nc contr | 21 | 1 | +0.05 | 0 | 0.3173 | 1.0000 | 0.00 | no |
| no glossary vs glossary, cloud | D7nc contr | 21 | 3 | -0.14 | 0 | 0.0833 | 1.0000 | 0.00 | no |
| post-processing (clean vs raw) | D7nc contr | 21 | 11 | -0.95 | 0 | 0.0025 | 0.0379 | 2.00 | no |
| thinking ON (clean) vs OFF, cloud | D7nc contr | 21 | 5 | +0.29 | 0 | 0.0339 | 0.4745 | 1.00 | no |

## Family: defect/echo (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| post-processing (clean vs raw) | D6 echo | 21 | 21 | -1.57 | 0 | <0.0001 | <0.0001 | 1.00 | YES |
| thinking ON (clean) vs OFF, cloud | D6 echo | 21 | 3 | +0.14 | 0 | 0.0833 | 0.0833 | 1.00 | no |

## Family: defect/num_lost (2 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| post-processing (clean vs raw) | D4 num | 21 | 6 | +0.52 | 0 | 0.0256 | 0.0339 | 3.00 | no |
| thinking ON (clean) vs OFF, cloud | D4 num | 21 | 7 | +0.76 | 0 | 0.0169 | 0.0339 | 2.95 | no |

## Family: defect/term_missing_nc (23 tests)

| contrast | metric | n | nonzero | Δ | W | p raw | p Holm | vs noise p95 | effect |
|---|---|---|---|---|---|---|---|---|---|
| thinking ON vs OFF, FP8 | D5nc term | 21 | 7 | -0.24 | 4 | 0.0588 | 1.0000 | 1.00 | no |
| thinking ON vs OFF, NVFP4 T=0.0 | D5nc term | 21 | 6 | +0.00 | 10 | 1.0000 | 1.0000 | 1.00 | no |
| thinking ON vs OFF, NVFP4 T=0.2 | D5nc term | 21 | 6 | -0.14 | 6 | 0.3173 | 1.0000 | 1.95 | no |
| thinking ON vs OFF, NVFP4 T=0.4 | D5nc term | 21 | 5 | -0.05 | 6 | 0.6547 | 1.0000 | 1.00 | no |
| thinking ON vs OFF, NVFP4 T=0.6 | D5nc term | 21 | 8 | -0.10 | 14 | 0.6078 | 1.0000 | 1.00 | no |
| thinking ON vs OFF, NVFP4 T=0.8 | D5nc term | 21 | 7 | -0.14 | 10 | 0.4290 | 1.0000 | 2.00 | no |
| thinking ON vs OFF, NVFP4 T=1.0 | D5nc term | 21 | 8 | -0.14 | 12 | 0.3657 | 1.0000 | 1.00 | no |
| FP8 vs cloud bf16, thinking OFF | D5nc term | 21 | 1 | +0.10 | 0 | 0.3173 | 1.0000 | 1.00 | no |
| NVFP4 vs FP8, thinking OFF | D5nc term | 21 | 3 | +0.14 | 0 | 0.0833 | 1.0000 | 1.00 | no |
| NVFP4 vs FP8, thinking ON | D5nc term | 21 | 7 | +0.24 | 6 | 0.1597 | 1.0000 | 1.95 | no |
| T=0.2 vs T=0 anchor, thinking OFF | D5nc term | 21 | 5 | +0.24 | 0 | 0.0253 | 0.5576 | 0.00 | no |
| T=0.2 vs T=0 anchor, thinking ON | D5nc term | 21 | 8 | +0.10 | 14 | 0.4795 | 1.0000 | 1.95 | no |
| T=0.4 vs T=0 anchor, thinking OFF | D5nc term | 21 | 4 | +0.19 | 0 | 0.0455 | 0.9100 | 0.00 | no |
| T=0.4 vs T=0 anchor, thinking ON | D5nc term | 21 | 10 | +0.14 | 20 | 0.4054 | 1.0000 | 1.00 | no |
| T=0.6 vs T=0 anchor, thinking OFF | D5nc term | 21 | 3 | +0.19 | 0 | 0.1025 | 1.0000 | 1.00 | no |
| T=0.6 vs T=0 anchor, thinking ON | D5nc term | 21 | 9 | +0.10 | 18 | 0.5637 | 1.0000 | 1.00 | no |
| T=0.8 vs T=0 anchor, thinking OFF | D5nc term | 21 | 5 | +0.24 | 0 | 0.0253 | 0.5576 | 0.00 | no |
| T=0.8 vs T=0 anchor, thinking ON | D5nc term | 21 | 7 | +0.10 | 10 | 0.5271 | 1.0000 | 2.00 | no |
| T=1.0 vs T=0 anchor, thinking OFF | D5nc term | 21 | 3 | +0.19 | 0 | 0.1025 | 1.0000 | 1.00 | no |
| T=1.0 vs T=0 anchor, thinking ON | D5nc term | 21 | 7 | +0.05 | 12 | 0.7055 | 1.0000 | 1.00 | no |
| no glossary vs glossary, cloud | D5nc term | 21 | 15 | +1.19 | 0 | 0.0005 | 0.0110 | 1.95 | no |
| post-processing (clean vs raw) | D5nc term | 21 | 4 | +0.24 | 0 | 0.0588 | 1.0000 | 1.95 | no |
| thinking ON (clean) vs OFF, cloud | D5nc term | 21 | 7 | +0.00 | 14 | 1.0000 | 1.0000 | 2.00 | no |

## Noise floor (T=0, greedy; server non-determinism)

| cond | MQM p95 of |Δrep| | MQM sd (mixed) | D3 code | D4 num | D5nc term | D6 echo | D7nc contr (pure repeat sd) |
|---|---|---|---|---|---|---|---|
| T00 off | 17.50 | 3.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T00 on | 35.00 | 8.70 | 0.16 | 0.00 | 0.16 | 0.00 | 0.00 |

_MQM sd (mixed) here is sd over the 3 repeat means (judges averaged); the STATUS.md column 'noise' is sd over all 6 scores (3 reps × 2 judges)._
