### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-consensus`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Требуется, когда `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: Уровень серьёзности|null}` — `Объект обсуждения_id` и `Уровень серьёзности` необязательны; остальное обязательно. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `Эскалация_id` | string | да | Формат идентификатора |
| `Сессия_id` | string | да | |
| `raised_by_Роль` | string | да | |
| `reason` | enum | да | `Эскалация_reason` |
| `Уровень_серьёзности` | enum | да | |
| `blocker` | string | да | 1–2000 символов |
| `positions` | object[] | да | `{Роль_id, Позиция, summary}` для каждой стороны |
| `operator_request` | string | да | Одно конкретное решение или отсутствующие данные |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `Резолюция` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_Фаза` | integer | да | Точная Фаза для возобновления |

