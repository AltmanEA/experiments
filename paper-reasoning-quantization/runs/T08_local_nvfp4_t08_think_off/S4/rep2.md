### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одному на активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие и `support`, и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: Уровень серьёзности|null}` — `subject_id` и `Уровень серьёзности` необязательны; остальное обязательно.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | yes | Формат идентификатора |
| `session_id` | string | yes | |
| `raised_by_role` | string | yes | |
| `reason` | enum | yes | `escalation_reason` |
| `severity` | enum | yes | |
| `blocker` | string | yes | 1–2000 символов |
| `positions` | object[] | yes | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | string | yes | Одно конкретное решение или отсутствие ввода |
| `fallback_strategy` | string | yes | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | yes | `null`, если срок не установлен |
| `resolution` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | yes | Точная фаза для возобновления |

