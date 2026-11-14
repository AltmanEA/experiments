### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одной для каждой активной роли; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, получившие и `support` и `oppose` в последнем раунде |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: Уровень серьёзности|null}` — `Объект обсуждения_id` и `Уровень серьёзности` опциональны; остальные обязательны. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `id_эскалации` | string | да | Формат идентификатора |
| `id_сессии` | string | да | |
| `роль_инициатора` | string | да | |
| `причина` | enum | да | `причина_эскалации` |
| `уровень_серьёзности` | enum | да | |
| `блокатор` | string | да | 1–2000 символов |
| `позиции` | object[] | да | `{id_роли, позиция, описание}` на каждую сторону |
| `запрос_оператора` | string | да | Одно конкретное решение или недостающие данные |
| `стратегия_резервного_варианта` | string | да | Что происходит, если оператор не отвечает |
| `время_таймаута` | timestamp \| null | да | `null`, если срок не установлен |
| `резолюция` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `фаза_возобновления` | integer | да | Точная фаза для возобновления |

