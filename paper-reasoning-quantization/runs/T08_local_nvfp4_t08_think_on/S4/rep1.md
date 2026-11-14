### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `условный`, `без-консенсуса`, `блокировка-эскалации` |
| `role_statuses` | RoleStatus[] | да | По одному на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Темы с блокирующим статусом |
| `disagreement_subjects` | string[] | да | Темы, имеющие и `поддержку`, и `против` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = блокировка-эскалации` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: ссылка-на-Объект-обсуждения|формат-обоснования|извлечение-статуса, Объект-обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: Уровень-серьёзности|null}` — `Объект-обсуждения_id` и `Уровень-серьёзности` необязательны; остальное обязательно.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | строка | да | Формат идентификатора |
| `session_id` | строка | да | |
| `raised_by_role` | строка | да | |
| `reason` | enum | да | `escalation_reason` |
| `severity` | enum | да | |
| `blocker` | строка | да | 1–2000 символов |
| `positions` | объект[] | да | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | строка | да | Одно конкретное решение или отсутствующие данные |
| `fallback_strategy` | строка | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null` при отсутствии дедлайна |
| `resolution` | объект | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | целое | да | Точная фаза для возобновления |

