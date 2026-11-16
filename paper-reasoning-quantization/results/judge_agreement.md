# Inter-judge agreement — judge_absolute.csv
judges: primary=gpt-oss-120b, secondary=gemma-4-31b
units (cond×fix×rep judged by both): 483; skipped (single-judge): 0

Pearson r           : 0.678
Spearman rho        : 0.726
weighted kappa (bands): 0.595
mean |Δ|            : 19.24  (median 12.0, p90 54.8, max 96)
signed Δ (prim−sec) : mean +9.66, sd 27.04; primary higher in 278, equal in 122, lower in 83

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
| FP8_T00_local_fp8_t00_think_off | 21 | 0.435 | 80.7 | 77.0 | +3.6 | 21.4 |
| FP8_T00_local_fp8_t00_think_on | 21 | 0.932 | 53.0 | 41.2 | +11.8 | 11.8 |
| FP8_T08_local_fp8_t08_think_off | 21 | 0.456 | 83.3 | 73.0 | +10.3 | 19.6 |
| FP8_T08_local_fp8_t08_think_on | 21 | 0.503 | 69.0 | 55.3 | +13.7 | 27.0 |
| K0_cloud_no_glossary | 21 | 0.371 | 80.3 | 74.5 | +5.8 | 19.0 |
| P8_cloud_fp8_think_off | 21 | 0.365 | 89.3 | 76.7 | +12.6 | 20.6 |
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
| S1 | 69 | 0.674 | -1.3 | 3.8 |
| S2 | 69 | 0.318 | +16.4 | 21.5 |
| S3 | 69 | 0.918 | +5.8 | 8.9 |
| S4 | 69 | 0.711 | +14.3 | 23.1 |
| S5 | 69 | 0.273 | -0.0 | 34.2 |
| S6 | 69 | 0.610 | +22.2 | 24.1 |
| S7 | 69 | 0.236 | +10.3 | 19.1 |

## Среднее vs консенсус (ранжирование условий)
Spearman rank corr vs two-judge mean: primary ρ=0.968, secondary ρ=0.944 (k=23 conditions)
conditions whose rank shifts under single-judge scoring: 17 — C1_cloud_bf16_think_off, C2_cloud_bf16_think_on, C3_local_fp8_think_off, C4_local_fp8_think_on, C5_local_nvfp4_think_off, C6_local_nvfp4_think_on, FP8_T00_local_fp8_t00_think_off, FP8_T00_local_fp8_t00_think_on, FP8_T08_local_fp8_t08_think_off, K0_cloud_no_glossary, P8_cloud_fp8_think_off, T00_local_nvfp4_t00_think_off, T00_local_nvfp4_t00_think_on, T04_local_nvfp4_t04_think_off, T08_local_nvfp4_t08_think_off, T10_local_nvfp4_t10_think_off, T10_local_nvfp4_t10_think_on

| condition | mean of judges | primary only | secondary only | max rank shift |
|---|---|---|---|---|
| T00_local_nvfp4_t00_think_off | 90.1 | 92.8 | 87.5 | 1 |
| T04_local_nvfp4_t04_think_off | 86.4 | 90.4 | 82.3 | 1 |
| C1_cloud_bf16_think_off | 85.6 | 88.3 | 82.9 | 2 |
| P8_cloud_fp8_think_off | 83.0 | 89.3 | 76.7 | 4 |
| C3_local_fp8_think_off | 82.5 | 95.9 | 69.1 | 7 |
| T06_local_nvfp4_t06_think_off | 82.4 | 85.9 | 79.0 | 0 |
| T08_local_nvfp4_t08_think_off | 82.3 | 83.6 | 81.0 | 2 |
| FP8_T00_local_fp8_t00_think_off | 78.9 | 80.7 | 77.0 | 1 |
| C5_local_nvfp4_think_off | 78.8 | 75.2 | 82.3 | 5 |
| FP8_T08_local_fp8_t08_think_off | 78.1 | 83.3 | 73.0 | 2 |
| K0_cloud_no_glossary | 77.4 | 80.3 | 74.5 | 2 |
| T10_local_nvfp4_t10_think_off | 75.8 | 78.0 | 73.7 | 2 |
| T08_local_nvfp4_t08_think_on | 71.0 | 76.6 | 65.4 | 0 |
| T10_local_nvfp4_t10_think_on | 69.4 | 78.2 | 60.6 | 3 |
| T06_local_nvfp4_t06_think_on | 62.9 | 70.1 | 55.7 | 0 |
| FP8_T08_local_fp8_t08_think_on | 62.2 | 69.0 | 55.3 | 0 |
| T04_local_nvfp4_t04_think_on | 60.1 | 69.0 | 51.3 | 0 |
| C4_local_fp8_think_on | 56.1 | 67.0 | 45.2 | 1 |
| C2_cloud_bf16_think_on | 52.7 | 55.9 | 49.6 | 1 |
| C6_local_nvfp4_think_on | 52.3 | 62.2 | 42.3 | 1 |
| FP8_T00_local_fp8_t00_think_on | 47.1 | 53.0 | 41.2 | 1 |
| T00_local_nvfp4_t00_think_on | 46.4 | 47.7 | 45.2 | 2 |
| C2_cloud_bf16_think_on_clean | 29.1 | 29.4 | 28.8 | 0 |
