### Вердикт консенсуса

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | yes | |
| `phase_id` | integer | yes | `4` |
| `outcome` | enum | yes | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | yes | По одной на каждую активную роль; без исключений |
| `blocking_subjects` | string[] | yes | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | yes | Субъекты, имеющие и `support`, и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | conditional | Требуется при `outcome = blocked-escalation` |
| `computed_at` | timestamp | yes | |

### Результат валидации

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: severity|null}` — `subject_id` и `severity` необязательны; остальное обязательно.

### Запись об эскалации

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | yes | Формат идентификатора |
| `session_id` | string | yes | |
| `raised_by_role` | string | yes | |
| `reason` | enum | yes | `escalation_reason` |
| `severity` | enum | yes | Уровень серьёзности |
| `blocker` | string | yes | 1–2000 символов |
| `positions` | object[] | yes | `{role_id, stance, summary}` для каждой стороны |
| `operator_request` | string | yes | Одно конкретное решение или недостающие данные |
| `fallback_strategy` | string | yes | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | yes | `null`, если срок не установлен |
| `resolution` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_phase` | integer | yes | Точная фаза для возобновления |

