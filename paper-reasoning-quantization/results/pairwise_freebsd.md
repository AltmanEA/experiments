# Pairwise: машинный вывод FreeBSD vs official RU (C3)

Условие A = машинный перевод, B = официальный RU-текст. «A» в verdict —
машина не хуже официального. reverse — контроль позиции (как в C1):
вердикт переложен обратно на условия.

| машинное условие | судья | порядок | n | A | tie | B | p vs 0.5 | verdict |
|---|---|---|---|---|---|---|---|---|
| F_C5_local_nvfp4_think_off-vs-REF_freebsd_official | gemma-4-31b | direct | 5 | 0 | 0 | 5 | 0.0625 | tie |
| F_C5_local_nvfp4_think_off-vs-REF_freebsd_official | gemma-4-31b | reverse | 5 | 0 | 0 | 5 | 0.0625 | tie |
| F_C5_local_nvfp4_think_off-vs-REF_freebsd_official | gpt-oss-120b | direct | 5 | 2 | 0 | 3 | 1.0000 | tie |
| F_C5_local_nvfp4_think_off-vs-REF_freebsd_official | gpt-oss-120b | reverse | 5 | 1 | 0 | 4 | 0.3750 | tie |
| **F_C5_local_nvfp4_think_off-vs-REF_freebsd_official** | **pooled (direct)** | — | **10** | **2** | **0** | **8** | **0.1094** | **tie** |

| F_C6_local_nvfp4_think_on-vs-REF_freebsd_official | gemma-4-31b | direct | 5 | 1 | 0 | 4 | 0.3750 | tie |
| F_C6_local_nvfp4_think_on-vs-REF_freebsd_official | gemma-4-31b | reverse | 5 | 0 | 0 | 5 | 0.0625 | tie |
| F_C6_local_nvfp4_think_on-vs-REF_freebsd_official | gpt-oss-120b | direct | 5 | 2 | 0 | 3 | 1.0000 | tie |
| F_C6_local_nvfp4_think_on-vs-REF_freebsd_official | gpt-oss-120b | reverse | 5 | 1 | 0 | 4 | 0.3750 | tie |
| **F_C6_local_nvfp4_think_on-vs-REF_freebsd_official** | **pooled (direct)** | — | **10** | **3** | **0** | **7** | **0.3438** | **tie** |

| F_T00_local_nvfp4_t00_think_off-vs-REF_freebsd_official | gemma-4-31b | direct | 5 | 0 | 0 | 5 | 0.0625 | tie |
| F_T00_local_nvfp4_t00_think_off-vs-REF_freebsd_official | gemma-4-31b | reverse | 5 | 0 | 0 | 5 | 0.0625 | tie |
| F_T00_local_nvfp4_t00_think_off-vs-REF_freebsd_official | gpt-oss-120b | direct | 5 | 1 | 0 | 4 | 0.3750 | tie |
| F_T00_local_nvfp4_t00_think_off-vs-REF_freebsd_official | gpt-oss-120b | reverse | 5 | 1 | 0 | 4 | 0.3750 | tie |
| **F_T00_local_nvfp4_t00_think_off-vs-REF_freebsd_official** | **pooled (direct)** | — | **10** | **1** | **0** | **9** | **0.0215** | **B** |

| F_T00_local_nvfp4_t00_think_on-vs-REF_freebsd_official | gemma-4-31b | direct | 5 | 2 | 0 | 3 | 1.0000 | tie |
| F_T00_local_nvfp4_t00_think_on-vs-REF_freebsd_official | gemma-4-31b | reverse | 5 | 2 | 0 | 3 | 1.0000 | tie |
| F_T00_local_nvfp4_t00_think_on-vs-REF_freebsd_official | gpt-oss-120b | direct | 5 | 4 | 0 | 1 | 0.3750 | tie |
| F_T00_local_nvfp4_t00_think_on-vs-REF_freebsd_official | gpt-oss-120b | reverse | 5 | 2 | 0 | 3 | 1.0000 | tie |
| **F_T00_local_nvfp4_t00_think_on-vs-REF_freebsd_official** | **pooled (direct)** | — | **10** | **6** | **0** | **4** | **0.7539** | **tie** |

Чтение: при доминировании официального RU и высоком chrF (83.6–84.7) вывод —
«машинный перевод близок к официальному, но стабильно уступает ему по
суждению судей»; доминирование A или ничьи означали бы, что судья не
различает тексты (ср. null-пробу C1: 40/40 tie при идентичных входах).
