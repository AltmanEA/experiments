### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-консенсус`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: Уровень серьёзности|null}` — `subject_id` и `Уровень серьёзности` необязательны; остальные обязательны. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `id_эскалации` | string | yes | Формат идентификатора |
| `id_сессии` | string | yes | |
| `поднято_ролью` | string | yes | |
| `reason` | enum | yes | `причина_эскалации` |
| `уровень_серьёзности` | enum | yes | |
| `blocker` | string | yes | 1–2000 символов |
| `positions` | object[] | yes | `{id_роли, позиция, краткое_описание}` для каждой стороны |
| `operator_request` | string | yes | Одно конкретное решение или отсутствующие данные |
| `fallback_strategy` | string | yes | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | yes | `null`, если срок не установлен |
| `резолюция` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `фаза_возобновления` | integer | yes | Точная фаза для возобновления |

