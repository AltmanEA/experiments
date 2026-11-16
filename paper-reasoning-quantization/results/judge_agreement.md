# Inter-judge agreement — judge_absolute.csv
judges: primary=gpt-oss-120b, secondary=gemma-4-31b
units (cond×fix×rep judged by both): 378; skipped (single-judge): 0

Pearson r           : 0.682
Spearman rho        : 0.715
weighted kappa (bands): 0.585
mean |Δ|            : 19.00  (median 12.0, p90 52.0, max 96)
signed Δ (prim−sec) : mean +9.44, sd 26.96; primary higher in 219, equal in 90, lower in 69

## By condition (Δ = primary − secondary)
| condition | n | r | mean prim | mean sec | mean Δ | mean |Δ| |
|---|---|---|---|---|---|---|
| C1_cloud_bf16_think_off | 21 | -0.076 | 88.3 | 82.9 | +5.5 | 16.0 |
| C2_cloud_bf16_think_on | 21 | -0.124 | 55.9 | 49.6 | +6.3 | 41.1 |
| C2_cloud_bf16_think_on_clean | 21 | 0.540 | 29.4 | 28.8 | +0.6 | 18.5 |
| C3_local_fp8_think_off | 21 | 0.500 | 95.9 | 69.1 | +26.8 | 28.0 |
| C4_local_fp8_think_on | 21 | 0.803 | 67.0 | 45.2 | +21.8 | 21.8 |
| C5_local_nvfp4_think_off | 21 | 0.483 | 75.2 | 82.3 | -7.0 | 19.4 |
| C6_local_nvfp4_think_on | 21 | 0.652 | 62.2 | 42.3 | +19.9 | 24.0 |
| K0_cloud_no_glossary | 21 | 0.371 | 80.3 | 74.5 | +5.8 | 19.0 |
| T00_local_nvfp4_t00_think_off | 21 | 0.184 | 92.8 | 87.5 | +5.2 | 12.1 |
| T00_local_nvfp4_t00_think_on | 21 | 0.932 | 47.7 | 45.2 | +2.5 | 9.4 |
| T04_local_nvfp4_t04_think_off | 21 | 0.537 | 90.4 | 82.3 | +8.0 | 13.1 |
| T04_local_nvfp4_t04_think_on | 21 | 0.758 | 69.0 | 51.3 | +17.6 | 23.3 |
| T06_local_nvfp4_t06_think_off | 21 | 0.756 | 85.9 | 79.0 | +7.0 | 12.3 |
| T06_local_nvfp4_t06_think_on | 21 | 0.901 | 70.1 | 55.7 | +14.4 | 14.4 |
| T08_local_nvfp4_t08_think_off | 21 | 0.193 | 83.6 | 81.0 | +2.7 | 20.4 |
| T08_local_nvfp4_t08_think_on | 21 | 0.900 | 76.6 | 65.4 | +11.2 | 12.6 |
| T10_local_nvfp4_t10_think_off | 21 | 0.688 | 78.0 | 73.7 | +4.3 | 17.5 |
| T10_local_nvfp4_t10_think_on | 21 | 0.855 | 78.2 | 60.6 | +17.6 | 19.0 |

## By fixture
| fixture | n | r | mean Δ | mean |Δ| |
|---|---|---|---|---|
| S1 | 54 | 0.678 | -1.4 | 4.3 |
| S2 | 54 | 0.347 | +14.2 | 20.5 |
| S3 | 54 | 0.917 | +6.6 | 8.8 |
| S4 | 54 | 0.727 | +10.3 | 21.6 |
| S5 | 54 | 0.316 | +2.3 | 32.5 |
| S6 | 54 | 0.645 | +22.4 | 23.7 |
| S7 | 54 | 0.224 | +11.8 | 21.6 |

## Среднее vs консенсус (ранжирование условий)
Spearman rank corr vs two-judge mean: primary ρ=0.959, secondary ρ=0.955 (k=18 conditions)
conditions whose rank shifts under single-judge scoring: 14 — C1_cloud_bf16_think_off, C2_cloud_bf16_think_on, C3_local_fp8_think_off, C4_local_fp8_think_on, C5_local_nvfp4_think_off, C6_local_nvfp4_think_on, K0_cloud_no_glossary, T00_local_nvfp4_t00_think_off, T00_local_nvfp4_t00_think_on, T04_local_nvfp4_t04_think_off, T06_local_nvfp4_t06_think_off, T08_local_nvfp4_t08_think_off, T10_local_nvfp4_t10_think_off, T10_local_nvfp4_t10_think_on

| condition | mean of judges | primary only | secondary only | max rank shift |
|---|---|---|---|---|
| T00_local_nvfp4_t00_think_off | 90.1 | 92.8 | 87.5 | 1 |
| T04_local_nvfp4_t04_think_off | 86.4 | 90.4 | 82.3 | 1 |
| C1_cloud_bf16_think_off | 85.6 | 88.3 | 82.9 | 1 |
| C3_local_fp8_think_off | 82.5 | 95.9 | 69.1 | 5 |
| T06_local_nvfp4_t06_think_off | 82.4 | 85.9 | 79.0 | 1 |
| T08_local_nvfp4_t08_think_off | 82.3 | 83.6 | 81.0 | 1 |
| C5_local_nvfp4_think_off | 78.8 | 75.2 | 82.3 | 4 |
| K0_cloud_no_glossary | 77.4 | 80.3 | 74.5 | 1 |
| T10_local_nvfp4_t10_think_off | 75.8 | 78.0 | 73.7 | 1 |
| T08_local_nvfp4_t08_think_on | 71.0 | 76.6 | 65.4 | 0 |
| T10_local_nvfp4_t10_think_on | 69.4 | 78.2 | 60.6 | 3 |
| T06_local_nvfp4_t06_think_on | 62.9 | 70.1 | 55.7 | 0 |
| T04_local_nvfp4_t04_think_on | 60.1 | 69.0 | 51.3 | 0 |
| C4_local_fp8_think_on | 56.1 | 67.0 | 45.2 | 1 |
| C2_cloud_bf16_think_on | 52.7 | 55.9 | 49.6 | 1 |
| C6_local_nvfp4_think_on | 52.3 | 62.2 | 42.3 | 1 |
| T00_local_nvfp4_t00_think_on | 46.4 | 47.7 | 45.2 | 1 |
| C2_cloud_bf16_think_on_clean | 29.1 | 29.4 | 28.8 | 0 |
