### Outcome-to-Transition Table

-официальный" might be better. I'll use "Это основной справочник для маршрутизации результатов." Wait, "outcome" was translated as "результат" or "исход". In voting/consensus contexts, "outcome" is usually "результат". Let's use "результат".
 Let's check the exact phrasing: "maps each ... value to its next state transition and Причина эскалации"
 "В следующей таблице каждому значению `ConsensusVerdict.outcome` сопоставлен следующий переход состояния и причина эскалации (при необходимости)."
 "This is the canonical reference for outcome routing." -> "Это основной справочник для маршрутизации результатов."

 Combine: 
 В следующей таблице каждому значению `ConsensusVerdict.outcome` сопоставлен следующий переход состояния и причина эскалации (при необходимости). Это основной справочник для маршрутизации результатов.

4. **Check Constraints:**
 - Translated only text between ` `? Yes.
 - Kept markdown? Yes, backticks preserved.
 - Specific terms: "Причина эскалации" -> "причина эскалации" (checked)
 - Tone/Context: Technical documentation. Sounds correct.

 Let's refine slightly for better technical Russian flow:
 "В следующей таблице приведено сопоставление каждого замечания `ConsensusVerdict.outcome` со следующим переходом состояния и причиной эскалации (если применимо). Данный раздел является основным справочником для маршрутизации результатов."
 Or more literally: "В следующей таблице каждому значению `ConsensusVerdict.outcome` соответствует следующий переход состояния и причина эскалации (при необходимости). Это канонический справочник для маршрутизации результатов."
 "canonical reference" in software often means "official/authoritative reference". "Основной справочник" or "эталонный документ" works well. I'll stick with "Это основной справочник для маршрутизации результатов."

 Let's verify the exact wording against standard tech translation practices:
 "maps each X to Y" -> "сопоставляет каждое X с Y" or "в таблице показано соответствие между X и Y".
 "next state transition" -> "следующий переход состояния"
 "Причина эскалации" -> "причина эскалации"
 "(if applicable)" -> "(при необходимости)" or "(если применимо)"
 "canonical reference" -> "основной справочник" / "эталонная справка"
 "outcome routing" -> "маршрутизация результатов" / "распределение исходов"

 Draft:
 В следующей таблице каждому значению `ConsensusVerdict.outcome` сопоставлен следующий переход состояния и причина эскалации (при необходимости). Это основной справочник для маршрутизации результатов.

 Checks:
 - Markdown: `ConsensusVerdict.outcome` kept.
 - Terms: "причина эскалации" used.
 - Meaning: Accurate.
 - Style: Technical, clear.

 One minor adjustment: "canonical reference" might be better as "официальный справочник" or "эталонный источник". I'll use "это основной справочник". It's safe.
 Another option: "Это канонический справочник..." - actually "канонический" is widely understood in IT. I'll stick with "основной" or "эталонный". Let's go with "основной справочник".

 Final check of the prompt: "

| `ConsensusVerdict.outoutcome` | Next Фаза / state | Причина эскалации | Notes |
|----------------------------|-------------------|-------------------|-------|
| `consensus` | Фаза 5 (Формирование Резолюции) | — | Все участники согласились. Перейти к производству Артефакта. |
| `conditional` | Фаза 5 (Формирование Резолюции) | — | Замечания присутствуют, но ничего не блокирует. Зафиксировать оговорки и продолжить. |
| `no-consensus` | Фаза 3 (повторный вход в раунд обсуждения) | — | Бюджет не исчерпан; дополнительные раунды обсуждения могут разрешить вопрос. |
| `blocked-escalation` | `awaiting-operator` | `information-gap` \| `irresolvable-conflict` \| `risk-threshold-breach` | Протокол Эскалации активирован. См. §Протокол Эскалации ниже. |

Где:
- `` `no-Консенсус` `` применяется, когда остаётся бюджет `` `no_Консенсус` `` (переходы `Фаза_state` с 4 на 3 согласно контракту времени выполнения).
- Когда бюджет исчерпан, фактический результат эквивалентен `blocked-эскалация` с `reason = information-gap`.
- Отсутствие роли Core или некорректный формат статуса также перенаправляет к `blocked-escalation` с соответствующей причиной, проверяется независимо от данной таблицы.
