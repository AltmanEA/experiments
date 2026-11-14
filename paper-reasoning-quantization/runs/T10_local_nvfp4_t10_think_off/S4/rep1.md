### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: severity|null}` — `subject_id` и **Уровень серьёзности** необязательны; остальные — обязательны.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | строка | да | Формат идентификатора |
| `session_id` | строка | да | |
| `raised_by_role` | строка | да | |
| `reason` | enum | да | `escalation_reason` |
| `severity` | enum | да | |
| `blocker` | строка | да | 1–2000 символов |
| `positions` | object[] | да | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | строка | да | Одно конкретное решение или недостающие данные |
| `fallback_strategy` | строка | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `resolution` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная фаза для продолжения |

