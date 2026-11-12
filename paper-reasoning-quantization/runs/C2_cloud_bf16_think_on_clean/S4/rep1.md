### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |

|-------|------|----------|------|

| `Сессия_id` | строка | да | |

| `фаза_id` | integer | yes | `4` |

| `outcome` | enum | да | `consensus`, `conditional`, `no-consensus`, `blocked-escalation` |
По одной на каждую активную роль; без пропусков

| `Роль_statuses` | RoleStatus[] | yes | По одной на каждую активную роль; без пропусков |

 ```

 | `Роль_statuses` | RoleStatus[] | yes | One per active role; no omissions |

 ```

| `role_statuses` | RoleStatus[] | yes | По одной на каждую активную роль; без пропусков |


| `blocking_subjects` | string[] | yes | Предметы со статусом блокировки |
Темы, имеющие как `support`, так и `oppose` в финальном раунде" or "Предметы, получившие как `support`, так и `oppose` в финальном раунде

| `Расхождение_subjects` | string[] | yes | Темы, имеющие как `support`, так и `oppose` в финальном раунде |



### ValidationResult

### EscalationRecord

| Поле | Тип | Обязательно | Правило |

|-------|------|----------|------|
| `эскалация_id` | строка | да | Формат идентификатора |
| `session_id` | строка | да | |
| `raised_by_role` | строка | да | |
| `Уровень серьёзности` | enum | yes | |

| `operator_request` | string | да | Одно конкретное решение или недостающие входные данные |



| `fallback_strategy` | string | yes | Что происходит, если оператор не отвечает |

| `timeout_at` | timestamp \| null | да | `null`, если дедлайн не установлен |

| `Резолюция` | object | yes | \{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at\} |

 - Use specified translation? Yes, Резолюция -> Резолюция.

| `resume_phase` | integer | yes | Точная фаза для продолжения |
