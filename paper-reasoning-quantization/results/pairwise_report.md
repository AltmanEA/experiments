# Pairwise judge preferences (P-002a)

Binomial two-sided on A vs B (ties excluded, reported separately).
Triangulation column: sign of the absolute-MQM paired effect (positive delta = B better).

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

