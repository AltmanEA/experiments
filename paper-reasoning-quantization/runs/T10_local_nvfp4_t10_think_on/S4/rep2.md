### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `условный`, `отсутствие-консенсуса`, `блокировка-эскалации` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие одновременно `support` и `oppose` в финальном раунде, формирующие расхождение |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = блокировка-эскалации` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: объект-обсуждения-reference|justification-format|status-extraction, объект_обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), уровень_серьёзности: уровень_серьёзности|null}` — `объект_обсуждения_id` и `уровень_серьёзности` необязательные; остальное обязательно.

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
| `operator_request` | string | да | Одно конкретное решение или отсутствие данных |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null` при отсутствии срока |
| `resolution` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | да | Точная фаза для продолжения |

