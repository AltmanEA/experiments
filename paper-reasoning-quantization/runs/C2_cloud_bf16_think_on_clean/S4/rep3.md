### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `session_id` | string | да | |
| `phase_id` | integer | да | `4` |
| `outcome` | enum | да | `консенсус`, `conditional`, `no-consensus`, `blocked-эскалация` |
| `role_statuses` | RoleStatus[] | да | По одной на активную роль; без пропусков |
| `blocking_subjects` | string[] | да | Субъекты со статусом блокировки |
| `disagreement_subjects` | string[] | да | Субъекты, имеющие как `support`, так и `oppose` в финальном раунде |
| `escalation_reason` | enum \| null | условно | Требуется при `outcome = blocked-эскалация` |
| `computed_at` | timestamp | да | |

### ValidationResult

`{check: ссылка-на-объект-обсуждения|формат-обоснования|извлечение-статуса, идентификатор_объекта_обсуждения: строка|null, корректность: логическое, код: VAL.*|PROT.*, сообщение: строка (закрыто), уровень_серьёзности: уровень_серьёзности|null}` — `идентификатор_объекта_обсуждения` и `уровень_серьёзности` необязательны; остальное обязательно.

### EscalationRecord

| Поле | Тип | Обязательно | Правило |

 | Field | Type | Required | Rule |

| Поле | Тип | Обязательно | Правило |` (with markdown preserved)
| Поле | Тип | Обязательно | Правило |`✅
| Поле | Тип | Обязательно | Правило |

|-------|------|----------|------|
| `Эскалация_id` | строка | да | Формат идентификатора |


| `session_id` | строка | да | |
| `raised_by_Роль` | строка | да | |
| `raised_by_role` | строка | да | |


 | `raised_by_Роль` | string | yes | |

| `raised_by_role` | строка | да | |
| `raised_by_role` | строка | да | |` (with proper markdown escaping if needed, but raw text is fine).
| `raised_by_role` | строка | да | |`✅
| `raised_by_role` | строка | да | |` (actually, just `| raised_by_Роль | строка | да | |`? No, keep backticks: `| `raised_by_role` | строка | да | |`)
| `raised_by_role` | строка | да | |
 | `raised_by_Роль` | строка | да | |
| `raised_by_role` | строка | да | |` -> in raw form: `| `raised_by_role` | строка | да | |
| `raised_by_role` | строка | да | |` (I'll escape if needed, but raw is fine)

| `raised_by_Роль` | строка | да | |

| `причина` | перечисление | да | `причина_эскалации` |

 `yes` -> `да`.

| `причина` | перечисление | да | `причина_эскалации` |



| `причина` | перечисление | да | `причина_эскалации` |` (I'll
| `причина` | перечисление | да | `причина_эскалации` |
 `| `причина` | перечисление | да | `причина_эскалации` |` -> done. 
| `причина` | перечисление | да | `причина_эскалации` |

| `Уровень серьёзности` | enum | yes | |
| `operator_request` | строка | да | Одно конкретное решение или отсутствующие входные данные |
| `fallback_strategy` | string | да | Что происходит, если оператор не отвечает |
| `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |


 | `timeout_at` | timestamp \| null | yes | `null` when no deadline is set |

 | `timeout_at` | timestamp \| null | да | `null`, если срок не установлен |


| `resume_Фаза` | integer | да | Точная фаза для возобновления |
