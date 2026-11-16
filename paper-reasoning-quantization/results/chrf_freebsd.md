# chrF vs official RU reference (freebsd)

Metric: sacrebleu corpus chrF (beta=2, char n-grams 1..6),
one document per unit; condition value = mean over fixtures.

| condition | mean chrF | min fixture | max fixture |
|---|---|---|---|
| F_T00_local_nvfp4_t00_think_off | 84.74 | 81.10 | 87.05 |
| F_C5_local_nvfp4_think_off | 84.43 | 80.32 | 86.68 |
| F_T00_local_nvfp4_t00_think_on | 83.98 | 79.77 | 87.23 |
| F_C6_local_nvfp4_think_on | 83.64 | 78.97 | 87.22 |

## Per fixture

| condition | F1_config | F2_security | F3_disks | F4_network-servers | F5_firewalls |
|---|---|---|---|---|---|
| F_C5_local_nvfp4_think_off | 86.62 | 82.98 | 85.54 | 80.32 | 86.68 |
| F_C6_local_nvfp4_think_on | 87.22 | 78.97 | 84.10 | 80.90 | 86.99 |
| F_T00_local_nvfp4_t00_think_off | 87.05 | 82.95 | 85.91 | 81.10 | 86.70 |
| F_T00_local_nvfp4_t00_think_on | 87.22 | 79.77 | 84.18 | 81.52 | 87.23 |
