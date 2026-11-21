## Table 3. Condition quality: defects (per run) and MQM

| condition | D3 code | D4 num | D5nc term | D6 echo | D7nc contr | MQM mean | 95% CI | crit/run | n |
|---|---|---|---|---|---|---|---|---|---|
| C1 cloud bf16, off | 0.05 | 0.00 | 0.57 | 0.00 | 0.43 | **85.6** | 79.8–90.6 | 0.12 | 42 |
| C2 cloud bf16, on (raw) | 2.71 | 0.24 | 0.33 | 1.71 | 1.67 | **52.7** | 43.1–62.2 | 1.38 | 42 |
| C2c cloud bf16, on (clean) | 3.48 | 0.76 | 0.57 | 0.14 | 0.71 | **29.1** | 19.7–38.9 | 3.33 | 42 |
| K0 cloud, no glossary | 0.00 | 0.00 | 1.76 | 0.00 | 0.29 | **77.4** | 69.9–84.2 | 0.12 | 42 |
| C3 FP8, off | 0.48 | 0.00 | 0.67 | 0.00 | 0.48 | **82.5** | 74.5–89.8 | 0.36 | 42 |
| C4 FP8, on | 1.90 | 0.00 | 0.43 | 0.00 | 0.43 | **56.1** | 45.3–66.9 | 1.81 | 42 |
| C5 NVFP4, off (T=0.2) | 0.29 | 0.00 | 0.81 | 0.00 | 0.43 | **78.8** | 70.5–86.1 | 0.60 | 42 |
| C6 NVFP4, on (T=0.2) | 1.57 | 0.00 | 0.67 | 0.00 | 0.43 | **52.3** | 40.8–63.7 | 1.60 | 42 |
| P8 cloud FP8, off (P-008) | 0.24 | 0.00 | 0.62 | 0.00 | 0.43 | **83.0** | 75.3–89.7 | 0.38 | 42 |
| T00 NVFP4, off | 0.00 | 0.00 | 0.57 | 0.00 | 0.43 | **90.1** | 86.1–93.6 | 0.10 | 42 |
| T00 NVFP4, on | 2.71 | 0.00 | 0.57 | 0.00 | 0.43 | **46.4** | 34.3–58.3 | 3.24 | 42 |
| T04 NVFP4, off | 0.33 | 0.00 | 0.76 | 0.00 | 0.48 | **86.4** | 78.4–92.7 | 0.40 | 42 |
| T04 NVFP4, on | 1.81 | 0.00 | 0.71 | 0.00 | 0.43 | **60.1** | 48.7–71.4 | 1.43 | 42 |
| T06 NVFP4, off | 0.24 | 0.00 | 0.76 | 0.00 | 0.52 | **82.4** | 74.6–89.2 | 0.24 | 42 |
| T06 NVFP4, on | 1.76 | 0.00 | 0.67 | 0.00 | 0.43 | **62.9** | 51.1–74.0 | 1.83 | 42 |
| T08 NVFP4, off | 0.19 | 0.00 | 0.81 | 0.00 | 0.48 | **82.3** | 74.5–89.0 | 0.40 | 42 |
| T08 NVFP4, on | 1.90 | 0.00 | 0.67 | 0.00 | 0.43 | **71.0** | 60.6–80.5 | 1.36 | 42 |
| T10 NVFP4, off | 0.19 | 0.00 | 0.76 | 0.00 | 0.52 | **75.8** | 66.7–83.8 | 0.69 | 42 |
| T10 NVFP4, on | 2.43 | 0.00 | 0.62 | 0.00 | 0.48 | **69.4** | 58.6–79.8 | 1.12 | 42 |

## Table 4. Paired MQM effects (21 fixture x rep pairs, judges averaged)

| contrast | Δ MQM | 95% CI | W/T/L | n |
|---|---|---|---|---|
| thinking ON vs OFF, FP8 | -26.4 | -37.3 – -16.6 | 1/3/17 | 21 |
| thinking ON vs OFF, NVFP4 | -26.5 | -40.2 – -14.0 | 2/4/15 | 21 |
| no glossary vs glossary, cloud | -8.2 | -16.9 – -0.5 | 8/2/11 | 21 |
| thinking ON (clean) vs OFF, cloud | -56.5 | -68.3 – -44.4 | 0/0/21 | 21 |
| post-processing (clean vs raw) | -23.6 | -36.2 – -10.8 | 7/0/14 | 21 |
| NVFP4 vs FP8, thinking OFF | -3.7 | -9.3 – +1.6 | 7/3/11 | 21 |
| NVFP4 vs FP8, thinking ON | -3.8 | -17.1 – +7.6 | 9/4/8 | 21 |
| FP8 vs cloud bf16, thinking OFF | -3.1 | -8.4 – +2.1 | 6/4/11 | 21 |
| thinking ON vs OFF, NVFP4 T=0.0 | -43.7 | -59.7 – -28.1 | 2/2/17 | 21 |
| thinking ON vs OFF, NVFP4 T=0.2 | -26.5 | -40.2 – -14.0 | 2/4/15 | 21 |
| thinking ON vs OFF, NVFP4 T=0.4 | -26.2 | -40.2 – -13.3 | 5/1/15 | 21 |
| thinking ON vs OFF, NVFP4 T=0.6 | -19.5 | -32.6 – -8.0 | 4/3/14 | 21 |
| thinking ON vs OFF, NVFP4 T=0.8 | -11.3 | -25.8 – +3.0 | 6/2/13 | 21 |
| thinking ON vs OFF, NVFP4 T=1.0 | -6.4 | -16.6 – +2.5 | 7/4/10 | 21 |
| T=0.2 vs T=0 anchor, thinking OFF | -11.4 | -18.7 – -4.9 | 2/6/13 | 21 |
| T=0.2 vs T=0 anchor, thinking ON | +5.8 | -5.9 – +18.2 | 10/4/7 | 21 |
| T=0.4 vs T=0 anchor, thinking OFF | -3.8 | -11.0 – +1.8 | 6/4/11 | 21 |
| T=0.4 vs T=0 anchor, thinking ON | +13.7 | +3.6 – +24.9 | 13/4/4 | 21 |
| T=0.6 vs T=0 anchor, thinking OFF | -7.7 | -15.9 – -0.9 | 4/3/14 | 21 |
| T=0.6 vs T=0 anchor, thinking ON | +16.5 | +6.8 – +27.8 | 11/7/3 | 21 |
| T=0.8 vs T=0 anchor, thinking OFF | -7.9 | -14.2 – -2.1 | 4/4/13 | 21 |
| T=0.8 vs T=0 anchor, thinking ON | +24.6 | +9.1 – +42.0 | 12/5/4 | 21 |
| T=1.0 vs T=0 anchor, thinking OFF | -14.3 | -24.3 – -6.2 | 3/4/14 | 21 |
| T=1.0 vs T=0 anchor, thinking ON | +23.0 | +9.3 – +38.3 | 14/3/4 | 21 |

## Table 5. Temperature grid (NVFP4 local, MQM mean of judges)

| T | MQM off | noise off (mix/gen) | D3 off | wall off, s | MQM on | noise on (mix/gen) | D3 on | wall on, s |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 90.1 | 8.4 / 4.0 | 0.00 | 9 | 46.4 | 11.1 / 8.7 | 2.71 | 165 |
| 0.2 | 78.8 | 14.7 / 7.1 | 0.29 | 9 | 52.3 | 26.1 / 19.8 | 1.57 | 168 |
| 0.4 | 86.4 | 11.1 / 7.4 | 0.33 | 9 | 60.1 | 22.3 / 16.0 | 1.81 | 176 |
| 0.6 | 82.4 | 13.0 / 10.5 | 0.24 | 9 | 62.9 | 21.1 / 19.6 | 1.76 | 170 |
| 0.8 | 82.3 | 15.2 / 8.9 | 0.19 | 9 | 71.0 | 23.6 / 23.2 | 1.90 | 178 |
| 1.0 | 75.8 | 12.9 / 7.6 | 0.19 | 9 | 69.4 | 18.7 / 14.6 | 2.43 | 179 |

_noise mix = sd over 3 repeats x 2 judges (mixed generation + judge noise, as in STATUS.md P-004); noise gen = sd over judge-averaged repeats (generation/server noise only)._

## Table 6. Temperature grid on FP8 (P-006, legacy engine, MQM mean of judges)

| T | MQM off | noise off (mix/gen) | D3 off | wall off, s | MQM on | noise on (mix/gen) | D3 on | wall on, s |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 78.9 | 13.3 / 3.9 | 0.43 | 18 | 47.1 | 9.0 / 4.6 | 2.90 | 299 |
| 0.2 (C3/C4) | 82.5 | 16.9 / 5.1 | 0.48 | 18 | 56.1 | 20.2 / 12.1 | 1.90 | 299 |
| 0.8 | 78.1 | 18.9 / 15.4 | 0.81 | 18 | 62.2 | 23.3 / 12.7 | 2.57 | 315 |

### Table 6b. Paired MQM effects on FP8 (21 fixture x rep pairs)

| contrast | Δ MQM | 95% CI | W/T/L | n |
|---|---|---|---|---|
| thinking ON vs OFF, FP8 T=0.0 | -31.7 | -45.1 – -19.0 | 1/3/17 | 21 |
| thinking ON vs OFF, FP8 T=0.8 | -15.9 | -25.9 – -7.3 | 4/2/15 | 21 |
| T=0.8 vs T=0 anchor, FP8 thinking OFF | -0.7 | -9.0 – +9.0 | 6/4/11 | 21 |
| T=0.8 vs T=0 anchor, FP8 thinking ON | +15.1 | +4.8 – +26.8 | 13/4/4 | 21 |
| NVFP4 vs FP8, T=0.0 thinking OFF | +11.3 | +4.2 – +19.4 | 9/3/9 | 21 |
| NVFP4 vs FP8, T=0.0 thinking ON | -0.7 | -6.7 – +4.7 | 6/8/7 | 21 |
| T=0.0 vs T=0.2, FP8 thinking OFF (legacy engine) | -3.6 | -9.0 – +1.1 | 7/5/9 | 21 |
| T=0.8 vs T=0.2, FP8 thinking ON (legacy engine) | +6.1 | +1.9 – +10.9 | 14/3/4 | 21 |

### Table 6c. P-008: placement vs quantization (cloud FP8 anchor, 21 pairs)

| contrast | Δ MQM | 95% CI | W/T/L | n |
|---|---|---|---|---|
| local vs cloud FP8, thinking OFF (placement) | -0.5 | -5.8 – +4.5 | 10/3/8 | 21 |
| bf16 vs FP8, cloud thinking OFF (quantization) | +2.6 | -3.4 – +9.4 | 9/5/7 | 21 |

## Table 7. FreeBSD domain (P-005, NVFP4): defects, MQM, chrF vs official RU

| condition | D3 code | D4 num | D5nc term | D6 echo | D7nc contr | MQM mean | 95% CI | crit/run | chrF | n |
|---|---|---|---|---|---|---|---|---|---|---|
| F_C5 NVFP4, off (T=0.2) | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | **83.0** | 76.5–88.6 | 0.10 | 84.4 | 30 |
| F_C6 NVFP4, on (T=0.2) | 0.00 | 0.00 | 0.20 | 0.00 | 0.07 | **90.3** | 87.0–93.3 | 0.00 | 83.6 | 30 |
| F_T00 NVFP4, off (T=0.0) | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | **82.2** | 76.8–87.3 | 0.07 | 84.7 | 30 |
| F_T00 NVFP4, on (T=0.0) | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | **90.0** | 86.1–93.6 | 0.00 | 84.0 | 30 |
| REF official RU (human ceiling) | — | — | — | — | — | **92.2** | 83.8–98.2 | — | — | 10 |

_chrF = sacrebleu vs official RU reference (only FreeBSD domain has a human reference); MQM scale is shifted down ~7-9 pts even on the reference itself (judge ceiling, see judge_agreement.md) — compare MQM within domain only._
