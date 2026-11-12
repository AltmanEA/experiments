### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-консенсус`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной на активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты с обоими `support` и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (замазана), уровень серьёзности: уровень серьёзности|null}` — `Объект обсуждения_id` и `уровень серьёзности` необязательны; остальные обязательны. ``

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
| `operator_request` | string | да | Конкретное решение или отсутствие данных |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `resolution` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная фаза для возобновления |

