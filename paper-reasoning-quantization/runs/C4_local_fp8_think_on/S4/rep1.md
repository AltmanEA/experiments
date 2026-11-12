### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одному на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Обязательно при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`` `{check: Объект обсуждения-reference|justification-format|status-extraction, Объект обсуждения_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: строка (замазана), Уровень серьёзности: Уровень серьёзности|null}` — `id_объекта_обсуждения` и `уровень_серьёзности` необязательны; остальные обязательны. ``

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `эскалация_id` | строка | да | Формат идентификатора |
| `сессия_id` | строка | да | |
| `raised_by_роль` | строка | да | |
| `причина` | enum | да | `эскалация_reason` |
| `уровень_серьёзности` | enum | да | |
| `блокатор` | строка | да | 1–2000 символов |
| `позиции` | object[] | да | `{роль_id, позиция, summary}` для каждой стороны |
| `запрос_оператора` | строка | да | Одно конкретное решение или отсутствие ввода |
| `стратегия_резервного_варианта` | строка | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |
| `резолюция` | object | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |
| `resume_фаза` | integer | да | Точная фаза для возобновления |

