# Pairwise judge preferences (P-002a)

Binomial two-sided on A vs B (ties excluded, reported separately).
Triangulation column: sign of the absolute-MQM paired effect (positive delta = B better).
NOTE: main table = direct presentation order only (original P-002a). Per the C1 decision rule it is superseded by the union table below.
| contrast | judge | n | A | tie | B | p vs 0.5 | verdict | abs-MQM Δ (95% CI) | agree |
|---|---|---|---|---|---|---|---|---|---|
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gemma-4-31b | 21 | 21 | 0 | 0 | 0.0000 | A | -56.5 (-68.3…-44.4) | yes |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gpt-oss-120b | 21 | 21 | 0 | 0 | 0.0000 | A | -56.5 (-68.3…-44.4) | yes |
| **C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean** | **pooled** | **42** | **42** | **0** | **0** | **0.0000** | **A** | **-56.5** (-68.3…-44.4) | yes |

| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gemma-4-31b | 21 | 16 | 0 | 5 | 0.0266 | A | -26.4 (-37.3…-16.6) | yes |
| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gpt-oss-120b | 21 | 18 | 0 | 3 | 0.0015 | A | -26.4 (-37.3…-16.6) | yes |
| **C3_local_fp8_think_off-vs-C4_local_fp8_think_on** | **pooled** | **42** | **34** | **0** | **8** | **0.0001** | **A** | **-26.4** (-37.3…-16.6) | yes |

| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gemma-4-31b | 21 | 14 | 0 | 7 | 0.1892 | tie | -26.5 (-40.2…-14.0) | — |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gpt-oss-120b | 21 | 16 | 0 | 5 | 0.0266 | A | -26.5 (-40.2…-14.0) | yes |
| **C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on** | **pooled** | **42** | **30** | **0** | **12** | **0.0079** | **A** | **-26.5** (-40.2…-14.0) | yes |

| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gemma-4-31b | 21 | 12 | 0 | 9 | 0.6636 | tie | -43.7 (-59.7…-28.1) | — |
| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gpt-oss-120b | 21 | 17 | 0 | 4 | 0.0072 | A | -43.7 (-59.7…-28.1) | yes |
| **T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on** | **pooled** | **42** | **29** | **0** | **13** | **0.0195** | **A** | **-43.7** (-59.7…-28.1) | yes |

## Основной ряд: объединение прямого и обратного предъявления (C1)

Правило C1 не пройдено ни одним рядом (см. «Контроль позиции»):
pooled position bias = 0.262, McNemar p = 0.0026, знак совпал в
148/168 (88.1%). Значит за итоговые
вердикты принимаются наблюдения обоих порядков (по 4 на единицу:
2 порядка × 2 судьи); прямые pooled-вердикты выше помечены как
superseded. winner переложен на условия, поэтому «A лучше» сопоставимо.

| контраст | судья | n | A | tie | B | p vs 0.5 | verdict | abs-MQM Δ (95% CI) | agree |
|---|---|---|---|---|---|---|---|---|---|
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gemma-4-31b | 42 | 42 | 0 | 0 | 0.0000 | A | -56.5 (-68.3…-44.4) | yes |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gpt-oss-120b | 42 | 42 | 0 | 0 | 0.0000 | A | -56.5 (-68.3…-44.4) | yes |
| **C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean** | **pooled (union)** | **84** | **84** | **0** | **0** | **0.0000** | **A** | **-56.5** (-68.3…-44.4) | yes |

| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gemma-4-31b | 42 | 31 | 0 | 11 | 0.0029 | A | -26.4 (-37.3…-16.6) | yes |
| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gpt-oss-120b | 42 | 32 | 0 | 10 | 0.0009 | A | -26.4 (-37.3…-16.6) | yes |
| **C3_local_fp8_think_off-vs-C4_local_fp8_think_on** | **pooled (union)** | **84** | **63** | **0** | **21** | **0.0000** | **A** | **-26.4** (-37.3…-16.6) | yes |

| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gemma-4-31b | 42 | 26 | 0 | 16 | 0.1641 | tie | -26.5 (-40.2…-14.0) | — |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gpt-oss-120b | 42 | 28 | 0 | 14 | 0.0436 | A | -26.5 (-40.2…-14.0) | yes |
| **C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on** | **pooled (union)** | **84** | **54** | **0** | **30** | **0.0116** | **A** | **-26.5** (-40.2…-14.0) | yes |

| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gemma-4-31b | 42 | 24 | 0 | 18 | 0.4408 | tie | -43.7 (-59.7…-28.1) | — |
| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gpt-oss-120b | 42 | 31 | 0 | 11 | 0.0029 | A | -43.7 (-59.7…-28.1) | yes |
| **T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on** | **pooled (union)** | **84** | **55** | **0** | **29** | **0.0060** | **A** | **-43.7** (-59.7…-28.1) | yes |


## Контроль позиции (задача C1, PLAN §6.2: перестановка порядков, все 4 контраста)

Единица = (контраст, фикстура, повтор, судья). Прямой порядок — из P-002a,
обратный — `judge_batch.py --order reverse`; вердикт в обратном порядке
переложен обратно на условия, поэтому столбцы «условие A лучше» сопоставимы.
`slot A` — доля выборов, когда судья указал на **слот** A (до переклада):
при отсутствии смещения ≈ 0.5 и в прямом, и в обратном предъявлении.

| контраст | судья | n пар | A лучше (прям.) | A лучше (обр.) | slot A (прям.) | slot A (обр.) | position bias | McNemar p | знак совпал |
|---|---|---|---|---|---|---|---|---|---|
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gemma-4-31b | 21 | 21 | 21 | 1.00 | 0.00 | 0.500 | nan | 21/21 |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | gpt-oss-120b | 21 | 21 | 21 | 1.00 | 0.00 | 0.500 | nan | 21/21 |
| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gemma-4-31b | 21 | 16 | 15 | 0.76 | 0.29 | 0.238 | 1.0000 | 20/21 |
| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | gpt-oss-120b | 21 | 18 | 14 | 0.86 | 0.33 | 0.262 | 0.2188 | 15/21 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gemma-4-31b | 21 | 14 | 12 | 0.67 | 0.43 | 0.119 | 0.5000 | 19/21 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | gpt-oss-120b | 21 | 16 | 12 | 0.76 | 0.43 | 0.167 | 0.2188 | 15/21 |
| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gemma-4-31b | 21 | 12 | 12 | 0.57 | 0.43 | 0.071 | nan | 21/21 |
| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | gpt-oss-120b | 21 | 17 | 14 | 0.81 | 0.33 | 0.238 | 0.3750 | 16/21 |
| **все контрасты** | **pooled** | **168** | **135** | **121** | **0.80** | **0.28** | **0.262** | **0.0026** | **148/168** |

Правило решения (зафиксировано до прогона): если `position bias` < 0.05 и
McNemar p > 0.05, а согласованность знака ≥ 0.8 — порядок не влияет, pooled-
вердикты основной таблицы публикуются как есть; смещение репортится в подписи.
Иначе — основной вердикт пересчитывается на объединении прямого и обратного
предъявления (по 4 наблюдения на единицу), а исходный pooled-ряд помечается.


## Null-проба на ничьи (A vs A)

Один и тот же текст в обоих слотах: правильное поведение судьи — `tie`.
Доля ничьих здесь — верхняя граница того, что судья вообще умеет говорить
`tie`; «0 ничьих из 168» в основной таблице значит столько, сколько позволяет
эта граница.

| группа | судья | n | tie | A | B | доля tie |
|---|---|---|---|---|---|---|
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean::same_a | gemma-4-31b | 5 | 5 | 0 | 0 | 1.00 |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean::same_a | gpt-oss-120b | 5 | 5 | 0 | 0 | 1.00 |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean::same_b | gemma-4-31b | 5 | 5 | 0 | 0 | 1.00 |
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean::same_b | gpt-oss-120b | 5 | 5 | 0 | 0 | 1.00 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on::same_a | gemma-4-31b | 5 | 5 | 0 | 0 | 1.00 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on::same_a | gpt-oss-120b | 5 | 5 | 0 | 0 | 1.00 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on::same_b | gemma-4-31b | 5 | 5 | 0 | 0 | 1.00 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on::same_b | gpt-oss-120b | 5 | 5 | 0 | 0 | 1.00 |
| **все группы** | **pooled** | **40** | **40** | **0** | **0** | **1.00** |

## Проверка на длину вывода (verbosity confound, бесплатно)

Победитель pairwise против разницы длин |A|−|B|. Если победа объясняется
длиной, а не качеством, — это ограничение к §5.10. r_point — точечно-
бисериальная корреляция (победа B, lenB−lenA); `nan` = вердикт не варьировался
(все единицы в одну сторону), тогда читается колонка «побеждал более длинный».

| контраст | n пар | mean len A | mean len B | побеждал более длинный | r_point |
|---|---|---|---|---|---|
| C1_cloud_bf16_think_off-vs-C2_cloud_bf16_think_on_clean | 42 | 2455 | 3810 | 8/42 | +nan |
| C3_local_fp8_think_off-vs-C4_local_fp8_think_on | 42 | 2467 | 2439 | 30/42 | +0.14 |
| C5_local_nvfp4_think_off-vs-C6_local_nvfp4_think_on | 42 | 2467 | 2454 | 27/42 | +0.24 |
| T00_local_nvfp4_t00_think_off-vs-T00_local_nvfp4_t00_think_on | 42 | 2460 | 2455 | 29/42 | +0.30 |
