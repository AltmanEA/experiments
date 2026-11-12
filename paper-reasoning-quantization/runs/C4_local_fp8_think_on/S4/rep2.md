### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-консенсус`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной на активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие и `support`, и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: объект-обсуждения|формат-обоснования|извлечение-статуса, объект_обсуждения: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (закрытая), уровень_серьёзности: уровень_серьёзности|null}` — `объект_обсуждения` и `уровень_серьёзности` необязательные; остальные обязательные.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | да | Формат идентификатора |
| `session_id` | string | да | |
| `raised_by_role` | string | да | |
| `reason` | enum | да | `эскалация_reason` |
| `severity` | enum | да | |
| `blocker` | string | да | 1–2000 символов |
| `positions` | object[] | да | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | string | да | Одно конкретное решение или недостающие данные |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `resolution` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная Фаза для возобновления |

