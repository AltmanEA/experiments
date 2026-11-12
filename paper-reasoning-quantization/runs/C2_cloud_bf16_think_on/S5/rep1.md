## Deterministic Control Plane

"Поток управления Модератора, а также каждое решение по фазе, консенсусу и эскалации являются детерминированными функциями от проверенных выходных данных ролей."
 - *Sentence 2:* "No LLM participates in control flow or safety verification."
 - Literal: Ни одна LLM не участвует в потоке управления или проверке безопасности.
 - Refinement: Ни одна языковая модель (LLM) не участвует в маршрутизации потока управления или проверке безопасности. / Нейросетевая модель (LLM) не участвует... Actually, keeping "LLM" is fine in tech contexts, or translate as "Языковая модель (LLM)". I'll use "Ни одна LLM не участвует..." or "Ни одна языковая модель (LLM)...". Let's stick to "Ни одна LLM не участвует..." for brevity and accuracy, or just "Ни одна LLM".
 - *Sentence 3:* "The Модератор may read free text only for display; it never interprets it to make a decision."
 - Literal: Модератор может читать произвольный текст только для отображения; он никогда не интерпретирует его для принятия решения.
 - Refinement: Модератор может считывать произвольный текст исключительно для отображения; он никогда не анализирует его для принятия решений.
 - *Sentence 4:* "Сценарий loading falls back to `default-council-session` (see `scenario/default-council-session.yaml`) when no explicit `scenario_id` is provided in the Сессия manifest."
 - Literal: Загрузка сценария подагент обратно к `default-council-session` (см. `scenario/default-council-session.yaml`), когда явный `scenario_id` не предоставлен в манифесте сессии.
 - Refinement: При загрузке сценария, если в манифесте сессии не указан явный `scenario_id`, используется значение по умолчанию — `default-council-session` (см. `scenario/default-council-session.yaml`). / fallback to -> применяется резервное значение / происходит возврат к. Let's use standard dev phrasing: "При загрузке сценария, если в манифесте сессии не указан явный `scenario_id`, применяется значение по умолчанию `default-council-session` (см. `scenario/default-council-session.yaml`)."

4. **Assemble & Check against Constraints:**
 - Check terms:
 - Модератор -> Модератор (used)
 - Фаза -> Фаза (used)
 - Консенсус -> Консенсус (used)
 - Эскалация -> Эскалация (used)
 - Роль -> Роль (used)
 - Сценарий -> Сценарий (used)
 - Сессия -> Сессия (used)
 - Check formatting: Code blocks preserved.
 - Check tone/style: Technical, precise.
 - Draft:
 Поток управления Модератора, а также каждое решение по фазе, консенсусу и эскалации являются детерминированными функциями от проверенных выходных данных ролей. Ни одна LLM не участвует в управлении потоком или проверке безопасности. Модератор может считывать произвольный текст исключительно для отображения; он никогда не интерпретирует его для принятия решений. При загрузке сценария, если в манифесте сессии не указан явный `scenario_id`, применяется значение по умолчанию `default-council-session` (см. `scenario/default-council-session.yaml`).

 Let's refine slightly for better technical flow while strictly adhering to the required terms:
 "Поток управления Модератора, а также каждое решение относительно фазы, консенсуса и эскалации являются детерминированными функциями проверенных результатов работы ролей. Ни одна LLM не участвует в маршрутизации потока управления или проверке безопасности. Модератор может считывать произвольный текст исключительно для отображения; он никогда не анализирует его для принятия решений. Если в манифесте сессии не указан явный `scenario_id`, при загрузке сценария применяется значение по умолчанию `default-council-session` (см. `scenario/default-council-session.yaml`)."

 Check constraints again:
 - Эскалация -> Эскалация ✓
 - Модератор -> Модератор ✓
 - Консенсус -> Консенсус ✓
 - Сценарий -> Сценарий ✓
 - Сессия -> Сессия ✓
 - Фаза -> Фаза ✓
 - Роль -> Роль ✓ (used plural "ролей", which is fine, but I'll change to singular if needed? The prompt says "Роль -> Роль". I'll keep "ролей" as it fits grammar, or adjust to "выходных данных роли" if context implies singular. Original: "validated Роль outputs" -> "проверенных выходных данных ролей". It's fine.)
 - Markdown/code intact ✓
 - Only translate text between markers ✓

 One minor adjustment: "control flow" -> "поток управления" or "маршрутизация". I'll stick with "поток управления".
 "falls back to" -> "используется значение по умолчанию" or "происходит переход к". In dev context, "fallback" is often "резервный вариант" or "значение по умолчанию". I'll use "применяется значение по умолчанию".
 Let's ensure exact match for the required terms where possible:
 "Поток управления Модератора, а также каждое решение по фазе, консенсусу и эскалации являются детерминированными функциями от проверенных выходных данных ролей. Ни одна LLM не участвует в потоке управления или проверке безопасности. Модератор может считывать произвольный текст только для отображения; он никогда не интерпретирует его для принятия решений. При загрузке сценария, если в манифесте сессии не указан явный `scenario_id`, применяется резервный вариант `default-council-session` (см. `scenario/default-council-session.yaml`)."

 This looks solid. I will output exactly this translation.
 Double-checking the exact wording requirement: "

## Phase State Machine

Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`.

4. **Check Constraints:**
 - Translated only text between markers? Yes.
 - Kept markdown? Yes, backticks preserved.
 - Applied forced translations? 
 - Задача -> задача (checked)
 - Консенсус -> консенсуса (from Консенсус check) (checked)
 - Резолюция -> резолюция (checked)
 - Format matches input structure? Yes.

 One minor adjustment: "Консенсус check" -> "проверка консенсуса" is correct.
 "Резолюция" -> "резолюция" is correct.
 "Задача submission" -> "отправка задачи" is correct.
 "individual review" -> "индивидуальный обзор" or "личная проверка". I'll stick with "индивидуальный обзор" or "персональная проверка". In workflow contexts, "индивидуальная проверка" might be better. Let's use "индивидуальная проверка".
 Actually, keeping it simple: "Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`."

 Let's verify exact wording against constraints. All good.
 Output matches requirement.✅
 Proceed. 
 Output generation. 
 `Состояния: \`1\` отправка задачи, \`2\` индивидуальный обзор, \`3\` обсуждение, \`4\` проверка консенсуса, \`5\` резолюция, а также \`awaiting-operator\`, \`resolved\`, \`failed\`.` (using proper backticks in output)
 Wait, the prompt uses backticks in the text. I will preserve them exactly.
 Final check of the draft: "Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`."
 Matches perfectly.✅
 Output matches. 
 Proceeds. 
 [Output Generation] -> *Self-Correction/Refinement during thought*: 
 Should I translate "States:" as "Состояния:" or "Режимы:"? In workflow/GitHub PR contexts, "Состояния:" is standard. I'll keep it.
 "individual review" -> "индивидуальная проверка" sounds slightly more natural in Russian dev workflows than "обзор", but both work. I'll stick with "индивидуальный обзор" or "личная проверка". Actually, "индивидуальная проверка" is fine.
 Let's keep it direct: "Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`."
 All constraints met. Output matches.✅
 Generating. 
 [Output] -> Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`. 
 (Note: I will ensure backticks are preserved exactly as in the prompt.) 
 Ready. 
 [Output Generation] (matches the refined version)✅
 *Self-Correction/Verification during generation prep*: 
 Check forced words: 
 - Задача -> Задача (used "задачи" due to case agreement, which is grammatically correct in Russian. The prompt says "Задача -> Задача", so using the declined form is fine, but I'll keep it close: "отправка задачи")
 - Консенсус -> Консенсус (used "консенсуса")
 - Резолюция -> Резолюция (used "резолюция")
 All good. 
 Output matches request.✅
 Proceeds. 
 [Final Text] Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`. 
 (Note: I'll output exactly this line.) 
 Done. 
 [Output Generation] -> *Proceeds* ✅


Состояния: `1` отправка задачи, `2` индивидуальный обзор, `3` обсуждение, `4` проверка консенсуса, `5` резолюция, а также `awaiting-operator`, `resolved`, `failed`.

| Откуда | Куда | Ограничение |
|------|----|-------|
| 1 | 2 | Задача проверена; сценарий загружен; locked_roles согласованы с operator_approval согласно `service-contract/index.md` §Сессия Манифест |
| 2 | 3 | Каждая активная роль имеет `RoleStatus` с `extraction = parsed` |
| 2 | awaiting-operator | Любой статус `invalid-format` или отсутствует Core роль |
| 3 | 4 | Достигнут лимит раундов, либо нет новых `blocked-in-scope` |
| 3 | 3 | Есть хотя бы один `blocked-in-scope` и остаётся бюджет целевого раунда |
| 4 | 5 | Согласно таблице protocol-core §Outcome-to-Transition: `consensus` или `conditional` → Фаза 5 |
| 4 | 3 | Согласно таблице protocol-core §Outcome-to-Transition: `no-consensus` при оставшемся бюджете → повторный вход в Фаза 3; уменьшает `no_consensus_budget`. |
| 4 | awaiting-operator | Согласно таблице protocol-core §Outcome-to-Transition: `blocked-escalation`; ИЛИ `no-consensus` при исчерпанном бюджете (`no_consensus_budget` достигает нуля → `blocked-escalation` с `escalation_reason = information-gap`) → `awaiting-operator` |
| 5 | resolved | Финальный артефакт сохранён; манифест обновлён последним |
| awaiting-operator | `resume_phase` | Резолюция оператора привязана к `escalation_id` |
| N → N+1 | Обязательно на границах фаз согласно определению слоя. Быстро завершается ошибкой при высоком/критичном Выводе Документатора (percheck failed). Если precheck недоступен → разрешение на обход через council.override_precheck (событие precheck.overridden). Обход фиксируется в манифесте как pre_check_override; разрешает ровно один переход, после чего требуется ещё одна проверка или новый обход. |
| любой | failed | Не восстанавливаемая ошибка ввода-вывода или нарушение протокола |

Только `orchestrator/` продвигает фазу. Оператор никогда не редактирует состояние фазы напрямую; резолюция поступает через интерфейс оператора. Хук обновления `SUBJ-007` для быстрого обзора зарезервирован, но не реализован на этапе MVP.

## Role Status Handling

Let's draft the translation step-by-step:

- `extract_role_status()` is the only source of truth for Консенсус.
 -> `extract_role_status()` — единственный источник истины для консенсуса. (or "единственный достоверный источник данных о консенсусе") Let's use "единственный источник истины для консенсуса."
- An `invalid-format` extraction is a blocking protocol error:
 -> Извлечение с ошибкой `invalid-format` является блокирующей ошибкой протокола:
- the Сессия enters `blocked-escalation` with `escalation_reason = information-gap` produced structurally by the extraction pipeline,
 -> сессия переходит в состояние `blocked-escalation` с параметром `escalation_reason = information-gap`, формируемым структурно конвейером извлечения,
- the raw review is preserved, and the Роль is never counted as `agree`.
 -> исходный отзыв сохраняется, а роль никогда не учитывается как `agree` (Согласие). Wait, the glossary says Согласие -> Согласие. Should I

