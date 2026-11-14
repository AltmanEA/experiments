### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
| `role_statuses` | RoleStatus[] | да | По одному на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие и `support`, и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = blocked-escalation` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: subject-reference|justification-format|status-extraction, subject_id: string|null, valid: boolean, code: VAL.*|PROT.*, message: string (redacted), severity: severity|null}` — `subject_id` и `Уровень серьёзности` опциональны; остальные обязательны.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `id_эскалации` | string | да | Формат идентификатора |
| `id_сессии` | string | да | |
| `повышено_ролью` | string | да | |
| `причина` | enum | да | `причина_эскалации` |
| `уровень_серьёзности` | enum | да | |
| `блокатор` | string | да | 1–2000 знаков |
| `позиции` | object[] | да | `{id_роли, позиция, описание}` на каждую сторону |
| `запрос_оператора` | string | да | Конкретное решение или отсутствующие данные |
| `резервная_стратегия` | string | да | Что происходит, если оператор не отвечает |
| `дата_окончания` | timestamp \| null | да | `null`, если срок не установлен |
| `резолюция` | object | да | `{состояние: ожидание\|принято\|отклонено\|заменено\|истекло, заметка, id_оператора, дата_исполнения}` |
| `фаза_возобновления` | integer | да | Точная фаза для возобновления |

