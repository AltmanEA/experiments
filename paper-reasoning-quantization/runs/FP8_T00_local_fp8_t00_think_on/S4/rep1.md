### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `условный`, `без-консенсуса`, `блокировка-эскалации` |
| `role_statuses` | RoleStatus[] | да | По одной на активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты с обоими `support` и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = блокировка-эскалации` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), Уровень серьёзности: Уровень серьёзности|null}` — `Объект обсуждения_id` и `Уровень серьёзности` необязательны; остальные обязательны. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `id_эскалации` | string | yes | Формат идентификатора |
| `id_сессии` | string | yes | |
| `роль_инициатора` | string | yes | |
| `причина` | enum | yes | `reason_эскалации` |
| `уровень_серьёзности` | enum | yes | |
| `блокатор` | string | yes | 1–2000 символов |
| `позиции` | object[] | yes | `{role_id, позиция, summary}` для каждой стороны |
| `запрос_оператора` | string | yes | Одно конкретное решение или отсутствующие данные |
| `стратегия_резервного_варианта` | string | yes | Что происходит, если оператор не отвечает |
| `время_тайм-аута` | timestamp \| null | yes | `null`, если срок не установлен |
| `резолюция` | object | yes | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `фаза_возобновления` | integer | yes | Точная фаза для возобновления |

