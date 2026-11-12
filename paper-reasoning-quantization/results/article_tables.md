## Table 3. Condition quality: defects (per run) and MQM

| condition | D3 code | D4 num | D5nc term | D6 echo | D7nc contr | MQM mean | 95% CI | crit/run | n |
|---|---|---|---|---|---|---|---|---|---|
| C1 cloud bf16, off | 0.05 | 0.00 | 0.57 | 0.00 | 0.43 | **85.6** | 79.8–90.6 | 0.12 | 42 |
| C2 cloud bf16, on (raw) | 2.71 | 0.24 | 0.33 | 1.71 | 1.67 | **52.7** | 43.1–62.2 | 1.38 | 42 |
| C2c cloud bf16, on (clean) | 3.48 | 0.76 | 0.57 | 0.14 | 0.71 | **29.1** | 19.7–38.9 | 3.33 | 42 |
| K0 cloud, no glossary | 0.00 | 0.00 | 1.76 | 0.00 | 0.29 | **77.4** | 69.9–84.2 | 0.12 | 42 |
| C3 FP8, off | 0.48 | 0.00 | 0.67 | 0.00 | 0.48 | **82.5** | 74.5–89.8 | 0.36 | 42 |
| C4 FP8, on | 1.90 | 0.00 | 0.43 | 0.00 | 0.43 | **56.1** | 45.3–66.9 | 1.81 | 42 |
| C5 NVFP4, off | 0.29 | 0.00 | 0.81 | 0.00 | 0.43 | **78.8** | 70.5–86.1 | 0.60 | 42 |
| C6 NVFP4, on | 1.57 | 0.00 | 0.67 | 0.00 | 0.43 | **52.3** | 40.8–63.7 | 1.60 | 42 |

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
