# Влияние квантования и режима рассуждений на перевод технической документации

Исследование (`qwen3.6-35b-a3b` и её кванты NVFP4/FP8): как **thinking (режим рассуждений)**
и **квантование/размещение** влияют на качество RU-перевода англоязычной технической
документации (домены: IT-контракты «Council», FreeBSD Handbook). Гипотезы H1–H5, метрики
дефектов D1–D9, судейство двумя LLM-судьями по MQM + pairwise.

**Главный вывод:** thinking=on портит вывод на квантованных серверах (MQM −26…−44,
порча contract-токенов ×4–5), особенно при greedy (T=0); лучшее условие статьи —
**greedy + thinking=off** (MQM 90.1). В контрактно-бедном домене FreeBSD инверсия
(+7.3) — boundary condition для H1/H2.

## Где что лежит

| Путь | Содержимое |
|---|---|
| `results/SUMMARY-RU.md` | статья-отчёт: гипотезы, §5 результаты, §8 выводы, §9 ограничения |
| `results/article_tables.md` | таблицы 3–7 (дефекты, MQM, парные эффекты, температура) |
| `results/figs/` | fig1–fig9 |
| `results/stats_tests{,_freebsd,_fp8,_p008}.md` | Wilcoxon + Holm, порог шума E-008 |
| `results/pairwise_report.md` | pairwise + контроль позиции + null-проба ничьих |
| `results/MANIFEST.sha256`, `results/VERSIONS.md` | контрольные суммы и версии окружения |
| `STATUS.md` | текущее состояние прогонов/судейства |
| `PLAN.md` | дизайн исследования (гипотезы, метрики, §6 требования к судейству) |
| `PLAN-CLOSEOUT.md` | **план оставшихся работ** (приоритеты [Б]/[Р]/[К]) |
| `NOTES.md` | журнал инцидентов и решений |
| `runs/<условие>/<фикстура>/rep<k>.md` | сырые переводы; `runs/progress_*.txt` — прогресс |
| `judge/<mode>/...` | сырые вердикты судей (resume-safe); `corpus/` — фикстуры и глоссарии |
| `metrics/` | весь анализ (скрипты stdlib+numpy; scipy/matplotlib — `.venv-analysis`) |
| `run_*.sh` | раннеры прогонов и судейства (gate по квоте провайдера, resume-safe) |

## Как воспроизвести

```bash
# окружение анализа (scipy/matplotlib/sacrebleu), один раз:
uv venv .venv-analysis && uv pip install --python .venv-analysis/bin/python \
  scipy matplotlib sacrebleu

# полная пересборка всех результатов из runs/ и judge/ (без GPU и облака):
bash metrics/rebuild_all.sh --figures
# после неё — проверка целостности:
( cd results && sha256sum -c MANIFEST.sha256 )
```

Исходные прогоны: локальные условия — `run_local_all.sh` / `run_progress.sh`
(vLLM-серверы NVFP4 :8000, FP8 :1919; стен-в-стену ≈9 с off / ≈170 с on на прогон);
облачные — `run_cloud.sh` / `cloud_paced.sh` (гейт квоты neuraldeep, ≤60 rpm);
судейство — `metrics/judge_batch.py` (см. `run_judge_20261116.sh`, `run_c1_position.sh`).

## Конвенции

- **MQM = среднее оценок двух судей** (gpt-oss-120b, gemma-4-31b); выбор схемы — §7 SUMMARY
  (ядро 18 условий: r = 0.682, взв. κ = 0.585; контроль на 23 условиях стабилен).
- **Эффект опубликован, если значим (p_holm) И выше шумового порога E-008.**
- Pairwise-вердикты — объединение прямого и обратного порядка предъявления
  (position bias 0.262 репортится; PLAN §6.2).
- `C2_cloud_bf16_think_on_clean` — C2 после `metrics/strip_trace.py` (облачный эндпоинт
  лил рассуждения в content; raw-вариант оставлен как характеристика дефекта).
