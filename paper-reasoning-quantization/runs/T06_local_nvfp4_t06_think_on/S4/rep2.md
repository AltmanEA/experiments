### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одной на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Вопросы со статусом блокировки |
| `disagreement_subjects` | string[] | да | Вопросы, получившие как `support`, так и `oppose` в последнем раунде |
| `escalation_reason` | enum \| null | по условию | Обязательно при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: severity|null}` — `subject_id` и `Уровень серьёзности` необязательны; остальные обязательны.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | да | Формат идентификатора |
| `session_id` | string | да | |
| `raised_by_role` | string | да | |
| `reason` | enum | да | `escalation_reason` |
| `Уровень серьёзности` | enum | да | |
| `blocker` | string | да | 1–2000 символов |
| `positions` | object[] | да | `{role_id, Позиция, summary}` для каждой стороны |
| `operator_request` | string | да | Конкретное решение или недостающие данные |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `Резолюция` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная фаза для возобновления |

