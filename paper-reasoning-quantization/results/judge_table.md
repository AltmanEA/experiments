| condition | judge | n | MQM mean | 95% CI | critical | major | minor |
|---|---|---|---|---|---|---|---|
| C1 cloud bf16, off | gemma-4-31b | 21 | 82.9 | 75.6–89.4 | 0.00 | 1.52 | 0.95 |
| C1 cloud bf16, off | gpt-oss-120b | 21 | 88.3 | 79.0–95.0 | 0.24 | 0.48 | 0.48 |
| C2 cloud bf16, on (raw) | gemma-4-31b | 21 | 49.6 | 37.7–60.1 | 1.86 | 0.57 | 0.43 |
| C2 cloud bf16, on (raw) | gpt-oss-120b | 21 | 55.9 | 40.0–70.8 | 0.90 | 2.67 | 0.48 |
| C2c cloud bf16, on (clean) | gemma-4-31b | 21 | 28.8 | 16.4–42.2 | 3.86 | 0.95 | 0.81 |
| C2c cloud bf16, on (clean) | gpt-oss-120b | 21 | 29.4 | 16.0–43.7 | 2.81 | 1.00 | 1.90 |
| K0 cloud, no glossary | gemma-4-31b | 21 | 74.5 | 64.7–84.1 | 0.05 | 2.24 | 0.95 |
| K0 cloud, no glossary | gpt-oss-120b | 21 | 80.3 | 69.2–89.6 | 0.19 | 1.48 | 1.05 |
| C3 FP8, off | gemma-4-31b | 21 | 69.1 | 56.0–81.7 | 0.71 | 1.24 | 0.33 |
| C3 FP8, off | gpt-oss-120b | 21 | 95.9 | 94.1–97.7 | 0.00 | 0.24 | 0.86 |
| C4 FP8, on | gemma-4-31b | 21 | 45.2 | 30.2–61.0 | 2.52 | 1.86 | 1.43 |
| C4 FP8, on | gpt-oss-120b | 21 | 67.0 | 53.2–79.6 | 1.10 | 0.52 | 0.90 |
| C5 NVFP4, off | gemma-4-31b | 21 | 82.3 | 75.0–89.1 | 0.19 | 1.19 | 0.52 |
| C5 NVFP4, off | gpt-oss-120b | 21 | 75.2 | 60.2–88.7 | 1.00 | 0.76 | 0.24 |
| C6 NVFP4, on | gemma-4-31b | 21 | 42.3 | 27.3–58.0 | 1.90 | 1.86 | 1.00 |
| C6 NVFP4, on | gpt-oss-120b | 21 | 62.2 | 46.5–77.7 | 1.29 | 0.95 | 1.05 |

| condition | n (all judges) | MQM mean | 95% CI |
|---|---|---|---|
| C1 cloud bf16, off | 42 | 85.6 | 79.7–90.5 |
| C2 cloud bf16, on (raw) | 42 | 52.7 | 43.0–62.2 |
| C2c cloud bf16, on (clean) | 42 | 29.1 | 20.1–38.6 |
| K0 cloud, no glossary | 42 | 77.4 | 70.0–84.1 |
| C3 FP8, off | 42 | 82.5 | 74.7–89.8 |
| C4 FP8, on | 42 | 56.1 | 45.6–66.7 |
| C5 NVFP4, off | 42 | 78.8 | 70.2–86.3 |
| C6 NVFP4, on | 42 | 52.3 | 41.5–63.7 |

Judge agreement (gemma-4-31b vs gpt-oss-120b), n=168 paired runs: mean |Δscore| = 23.5, Pearson r = 0.55, identical score = 23%.
