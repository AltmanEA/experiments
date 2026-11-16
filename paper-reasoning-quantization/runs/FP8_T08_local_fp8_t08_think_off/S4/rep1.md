### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `условный`, `нет-консенсуса`, `блокировка-эскалации` |
| `role_statuses` | RoleStatus[] | да | По одному для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие и `support`, и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно, когда `outcome = блокировка-эскалации` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: severity|null}` — `subject_id` и `Уровень серьёзности` необязательны; остальные обязательны.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | да | Формат идентификатора |
| `session_id` | string | да | |
| `raised_by_role` | string | да | |
| `reason` | enum | да | `escalation_reason` |
| `severity` | enum | да | |
| `blocker` | string | да | 1–2000 символов |
| `positions` | object[] | да | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | string | да | Одно конкретное решение или отсутствующий ввод |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, когда срок не установлен |
| `resolution` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная фаза для возобновления |

