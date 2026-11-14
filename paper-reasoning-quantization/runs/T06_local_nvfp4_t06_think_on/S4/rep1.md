### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `Консенсус`, `условный`, `без-консенсуса`, `заблокированная-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно, когда `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: severity|null}` — `subject_id` и `Уровень серьёзности` необязательны; остальные обязательны.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `эскалация_id` | string | yes | Формат идентификатора |
| `сессия_id` | string | yes | |
| `поднятая_ролью` | string | yes | |
| `reason` | enum | yes | `эскалация_reason` |
| `уровень_серьёзности` | enum | yes | |
| `blocker` | string | yes | 1–2000 символов |
| `positions` | object[] | yes | `{роль_id, позиция, summary}` для каждой стороны |
| `operator_request` | string | yes | Одно конкретное решение или отсутствие данных |
| `fallback_strategy` | string | yes | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | yes | `null`, если срок не установлен |
| `резолюция` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_фаза` | integer | yes | Точная фаза для возобновления |

