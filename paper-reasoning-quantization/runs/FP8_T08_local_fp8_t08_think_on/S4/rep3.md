### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-consensus`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие и `support` и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно, когда `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: Уровень серьёзности|null}` — `Объект обсуждения_id` и `Уровень серьёзности` опциональны; остальное обязательно. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `эскалация_id` | string | yes | Формат идентификатора |
| `сессия_id` | string | yes | |
| `инициировавший_ролью` | string | yes | |
| `причина` | enum | yes | `эскалация_причина` |
| `уровень_серьёзности` | enum | yes | |
| `блокатор` | string | yes | 1–2000 символов |
| `позиции` | object[] | yes | `{роль_id, позиция, краткое_описание}` для каждой стороны |
| `запрос_оператора` | string | yes | Одно конкретное решение или отсутствие ввода |
| `стратегия_замены` | string | yes | Что произойдёт, если оператор не ответит |
| `время_тайм_аута` | timestamp \| null | yes | `null` при отсутствии установленного срока |
| `резолюция` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `возобновление_фазы` | integer | yes | Точная фаза для возобновления |

