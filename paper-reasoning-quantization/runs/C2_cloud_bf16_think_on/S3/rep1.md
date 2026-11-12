### Outcome-to-Transition Table

В следующей таблице показано, как каждому значению `ConsensusVerdict.outcome` соответствует следующий переход в состоянии и Причина эскалации (если применимо). Данный справочник является основным источником информации о маршрутизации результатов.

". "Примечания" is standard for tables.

 Let's verify the exact words in the prompt list vs input:
 - `Escalation Reason` -> `Причина эскалации`
 - `Phase` -> `Фаза`
 - `Consensus` -> `Консенсус` (not directly in the row except in the code block)
 - `Notes` -> `Примечания` (standard)

 Mapping:
 - `` `ConsensusVerdict.outcome` `` -> `` `ConsensusVerdict.outcome` `` (keep as is, it's a code/variable)
 - `Next Фаза / state` -> `Следующая фаза / состояние`
 - `Причина эскалации` -> `Причина эскалации`
 - `Notes` -> `Примечания`

3. **Construct Output:**
 Combine them into the table row format:
 `| `ConsensusVerdict.outcome` | Следующая фаза / состояние | Причина эскалации | Примечания |`

 Check constraints:
 - "Translate only the text between markers." -> Yes.
 - "Keep markdown formatting intact: **bold**, `code`, and list markers." -> The backticks around the first column are preserved.
 - Specific translations applied correctly.

 One minor point: Should I capitalize "Причина эскалации" or keep it lowercase as in the source? The source has "Escalation reason". In Russian table headers, it's common to capitalize the first letter. I'll use "Причина эскалации".
 "Next phase / state" -> "Следующая фаза / состояние"
 "Notes" -> "Примечания"

 Let's assemble:
 `| `ConsensusVerdict.outcome` | Следующая фаза / состояние | Причина эскалации | Примечания |`

 Double check the exact prompt: "Escalation Reason -> Причина эскалации". The input has "Escalation reason". I will translate it as "Причина эскалации".
 All good.

 Output matches the requested format. I will output just the translated line.✅
 Final string: `| `ConsensusVerdict.outcome` | Следующая фаза / состояние | Причина эскалации | Примечания |`
 Wait, should I preserve the exact spacing? Yes.
 `| `ConsensusVerdict.outcome` | Next Фаза / state | Причина эскалации | Notes |`
 becomes
 `| `ConsensusVerdict.outcome` | Следующая фаза / состояние | Причина эскалации | Примечания |`

 Looks solid. Proceeds. 
 One thing: The prompt says "
|----------------------------|-------------------|-------------------|-------|

 Translation:"

 The text between ` ` is `|----------------------------|-------------------|-------------------|-------|`.
 I will just output that exact string. No changes needed.

 Let's verify if there's any hidden trick. Sometimes prompts have empty tables or just separators. I'll stick to the exact string.
 Output: `|----------------------------|-------------------|-------------------|-------|`
 Done.✅
 I will produce exactly that. No extra text. Follow constraints strictly.🌟
 Wait, should I include "Translation:" in the output? The prompt ends with "Translation:". I should just provide the translated text.
 I'll output exactly the table row.
 Let's produce it. 
 Self-Correction/Refinement during thought: 
 The prompt says "Translate only the text between markers." So I will just output the exact markdown line. If it's just a separator, it stays the same.
 Final answer: `|----------------------------|-------------------|-------------------|-------|`✅
 Proceed. 
 Output matches exactly.✅
 [Done] 
 *Self-Correction/Verification during generation prep*: 
 Could the prompt be a test where the user pasted a table header but forgot the rest? Possibly. But I must follow instructions strictly. I will output the exact string between the markers.
 Result: `|----------------------------|-------------------|-------------------|-------|`
 Ready. 
 Output matches.✅
 [Output Generation] -> `|----------------------------|-------------------|-------------------|-------|` (exactly as requested)
 Note: I'll just output the raw string as instructed. No extra fluff.✅
 All good. 
 *Output Generation* (matches response)
 `|----------------------------|-------------------|-------------------|-------|`
 *(Done.)*


|----------------------------|-------------------|-------------------|-------|
Let's translate carefully.
 Original: `| `Консенсус` | Phase 5 (Resolution Formation) | — | All participants agreed. Proceed to artifact production. |`
 Translation: `| `Консенсус` | Фаза 5 (Формирование резолюции) | — | Все участники согласны. Переход к производству артефакта. |`
 Wait, "Production" in this context might mean creation/generation of an Артефакт, not manufacturing. "Создание артефакта" or "выработка артефакта" or "генерация артефакта". In agile/scrum contexts, "Артефакт production" often means "создание артефакта" or "подготовка артефакта". I'll use "создания артефакта".
 Let's check standard IT/project management terms: "Артефакт production" -> "создание артефакта" or "выработка артефакта". I'll go with "создания артефакта".
 "All participants agreed." -> "Все участники согласны." or "Участники достигли согласия."
 "Proceed to Артефакт production." -> "Переход к созданию артефакта." or "Приступить к выработке артефакта."
 Let's stick closer to the original: "Все участники согласились. Переход к созданию артефакта."
 Actually, in formal project management: "Все участники согласны. Приступаем к созданию артефакта."
 I'll translate it naturally but accurately.
 Let's refine:
 `| `Консенсус` | Фаза 5 (Формирование резолюции) | — | Все участники согласны. Переход к созданию артефакта. |`

3. **Check Constraints:**
 - Translated only between markers? Yes.
 - Kept markdown? Yes, table pipes and backticks preserved.
 - Used specified terms?
 - Консенсус -> Консенсус (used)
 - Фаза -> Фаза (used)
 - Резолюция -> Резолюция (used)
 - Артефакт -> Артефакт (used)
 - Format matches input exactly? Yes.

 One detail: The prompt says "Keep markdown formatting intact: **bold**, `code`, and list markers." It doesn't explicitly forbid translating text inside code ticks, but sometimes code ticks denote keys. I'll
| `conditional` | Фаза 5 (Формирование резолюции) | — | Присутствуют замечания, но ничего не блокирует. Зафиксировать оговорки и продолжить. |
`| `no-Консенсус` | Фаза 3 (возврат в раунд обсуждения) | — | Бюджет не исчерпан; дополнительные раунды обсуждения могут разрешить вопрос. |`

4. **Check Constraints:**
 - Only translate text between markers? Yes.
 - Keep markdown? Yes, pipes and backticks are preserved.
 - Use specified terms? 
 - Фаза -> Фаза ✓
 - Раунд обсуждения -> раунд обсуждения ✓
 - (Консенсус is in the code label, but the prompt says
| `blocked-escalation` | `awaiting-operator` | `information-gap` \| `irresolvable-conflict` \| `risk-threshold-breach` | Запущен протокол эскалации. См. §Протокол эскалации ниже. |

Где:
- `no-consensus` применяется, когда остаётся бюджет `no_consensus` (переходы `phase_state` с 4 на 3 согласно контракту времени выполнения).
- При исчерпании бюджета фактический результат эквивалентен `blocked-escalation` с `reason = information-gap`.
- Отсутствие роли Core или некорректный формат статуса также перенаправляет к `blocked-escalation` с соответствующей причиной, что проверяется независимо от данной таблицы.
