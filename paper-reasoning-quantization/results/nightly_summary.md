# Nightly run summary

Log: `runs/nightly_20261115-163605.log`

Notable log lines:
- [16:39:47] ALL DONE 15/15
- [17:47:46] ALL DONE 15/15
- [17:51:25] ALL DONE 15/15
- [19:24:37] ALL DONE 15/15
- [trace] ALL DONE
- [trace] ALL DONE

## P-005 runs (FreeBSD domain)

| condition | runs | expected | wall mean, s | exit≠0 |
|---|---|---|---|---|
| F_C5_local_nvfp4_think_off | 15 | 15 | 14.7 | 3 |
| F_C6_local_nvfp4_think_on | 15 | 15 | 271.9 | 3 |
| F_T00_local_nvfp4_t00_think_off | 15 | 15 | 14.5 | 3 |
| F_T00_local_nvfp4_t00_think_on | 15 | 15 | 372.8 | 5 |

**Total: 60/60 runs.**

## P-007 reasoning traces

| condition | fixture | rep | requests | reasoning chars | content chars | wall, s |
|---|---|---|---|---|---|---|
| TRACE_S4_local_nvfp4_t00_think_on | S4 | 1 | 8 | 71072 | 1778 | 180.9 |
| TRACE_S4_local_nvfp4_t00_think_on | S4 | 2 | 8 | 71072 | 1778 | 180.8 |
| TRACE_S4_local_nvfp4_t00_think_on | S4 | 3 | 8 | 71072 | 1778 | 181.0 |
| TRACE_S5_local_nvfp4_t00_think_on | S5 | 1 | 9 | 107484 | 3645 | 275.1 |
| TRACE_S5_local_nvfp4_t00_think_on | S5 | 2 | 9 | 109214 | 3646 | 278.8 |
| TRACE_S5_local_nvfp4_t00_think_on | S5 | 3 | 9 | 109214 | 3646 | 278.8 |

## Defect metrics (FreeBSD, per run)

| condition | D3 code | D5nc term | D7nc contr | D4 num | D6 echo | FAIL | wall, s |
|---|---|---|---|---|---|---|---|
| F_C5_local_nvfp4_think_off | 0.00 | 2.20 | 2.20 | 0.00 | 0.00 | 0.20 | 14.7 |
| F_C6_local_nvfp4_think_on | 0.00 | 2.13 | 2.27 | 0.00 | 0.00 | 0.20 | 271.9 |
| F_T00_local_nvfp4_t00_think_off | 0.00 | 2.20 | 2.20 | 0.00 | 0.00 | 0.20 | 14.5 |
| F_T00_local_nvfp4_t00_think_on | 0.00 | 2.00 | 2.20 | 0.00 | 0.00 | 0.33 | 372.8 |

## chrF vs official RU reference


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

## MQM absolute (FreeBSD)

_no P-005 conditions judged yet — run `bash run_nightly.sh --judge-only`_
