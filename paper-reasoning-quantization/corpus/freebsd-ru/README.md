# FreeBSD Handbook — второй домен (EN→RU)

Источники: [freebsd/freebsd-doc](https://github.com/freebsd/freebsd-doc)
(AsciiDoc → Markdown конвертация).

## Структура

```
freebsd-ru/
├── source/          # Английские исходники для перевода
│   ├── F1_config.md           # Глава 14. Configuration, Services, Logging and Power Management
│   ├── F2_security.md         # Глава 16. Security
│   ├── F3_disks.md            # Глава 21. Disks
│   ├── F4_network-servers.md  # Глава 33. Network Servers
│   └── F5_firewalls.md        # Глава 34. Firewalls
├── reference/       # Официальные RU-переводы (для калибровки/валидации)
│   ├── F1_config.md
│   ├── F2_security.md
│   ├── F3_disks.md
│   ├── F4_network-servers.md
│   └── F5_firewalls.md
├── gloss_pairs/     # Пары EN→RU по главам (F1_config.txt ... F5_firewalls.txt)
├── glossary.md      # Сводный глоссарий домена
└── README.md        # этот файл
```

## Характеристики домена

- **Техническая документация ОС** — системное администрирование, конфигурация, безопасность
- **Стили текста**: процедурные (config), концептуальные (security overview), структурные (tables, code blocks)
- **Наличие code-токенов**: ✅ shell-команды, sysctl-переменные, man-страницы
- **Наличие таблиц**: ✅ конфигурационные таблицы, параметры
- **Числа/даты/идентификаторы**: ✅ порты, версии, пути, квоты
- **Глоссарий**: нужен собственный (FreeBSD-терминология: jail, ZFS, PF, sysctl и т.д.)

## Использование

Для эксперимента (PLAN.md):
- `source/*` — EN-исходники, аналогично S1–S7 из Council
- `reference/*` — RU-эталонные переводы (для калибровки LLM-судьи)
- `glossary.md` + `gloss_pairs/F*.txt` — пары EN→RU в формате судьи (`EN -> RU`)
- `glossary_pipeline.md` — тот же глоссарий в формате пайплайна (`**EN** (RU)`),
  образуется `metrics/glossary_to_pipeline.py`; именно его подавать в `GLOSS=`

### Прогон (второй домен)

```bash
# глоссарий для пайплайна и метрик D5/D7 (регенерировать после правки пар)
python3 ../../metrics/glossary_to_pipeline.py

# перевод: GLOSS — pipeline-глоссарий, CORPUS_DIR — каталог с F-фикстурами
GLOSS=$PWD/glossary_pipeline.md CORPUS_DIR=corpus/freebsd-ru/source \
  ../../run_progress.sh F_C5_local_nvfp4_think_off false Qwen3.6-35B-A3B-NVFP4 \
  "F1_config F2_security F3_disks F4_network-servers F5_firewalls"

# судейство: --tag изолирует выводы от таблиц Council
python3 ../../metrics/judge_batch.py --mode absolute --tag _freebsd \
  --fixtures F1_config F2_security F3_disks F4_network-servers F5_firewalls \
  --corpus-dir corpus/freebsd-ru/source --pairs-dir corpus/freebsd-ru/gloss_pairs \
  --conditions F_C5_local_nvfp4_think_off
```

Условия второго домена принято именовать с префиксом `F_`, чтобы они не смешивались
с `C*`/`T*` первого домена в `runs/` и сводных таблицах.

## Примечания

- Файлы конвертированы из AsciiDoc в Markdown (python-скрипт) и очищены от артефактов:
  удалены `toc::[]`, `[.filename]#/path#`, атрибутные блоки `[CAUTION]`/`[NOTE]`,
  таблицы `|===` приведены к pipe-формату Markdown.
- Объёмы: исходные главы ~1.2k–2k строк; в `source/` и `reference/` лежат готовые срезы
  54–62 строки на главу, выровненные построчно между EN и RU.
- `gloss_pairs/F*.txt` — пары EN→RU по каждой главе (тот же формат, что `corpus/gloss_pairs/S*.txt`);
  `glossary.md` — сводный глоссарий домена.
- Лицензия: FreeBSD Documentation Project (BCL, совместима с research).
