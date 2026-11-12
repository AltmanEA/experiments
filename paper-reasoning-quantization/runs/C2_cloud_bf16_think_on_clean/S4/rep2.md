### ConsensusVerdict

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|

| `phase_id` | целое число | да | `4` |

 | `Фаза_id` | целое число | да | `4` |

| `phase_id` | целое число | да | `4` |` (with proper formatting)
| `outcome` | enum | да | `консенсус`, `условный`, `без-консенсуса`, `блокировка-эскалации` |
| `Роль_statuses` | RoleStatus[] | да | По одной записи на каждую активную роль; без пропусков |
| `blocking_subjects` | string[] | yes | Темы со статусом блокировки |

| `blocking_subjects` | string[] | yes | Темы со статусом блокировки |` (or similar valid translation)
| `disagreement_subjects` | string[] | да | Субъекты с обоими вариантами `support` и `oppose` в финальной фазе |

| `Эскалация_reason` | enum \| null | условный | Требуется при `outcome = blocked-Эскалация` |

 `| escalation_reason | enum | null | conditional | Required when outcome = blocked-escalation |`

| `Эскалация_reason` | enum \| null | условный | Требуется при `outcome = blocked-Эскалация` |

| `computed_at` | метка времени | да | |

### ValidationResult

### EscalationRecord

| Поле | Тип | Обязательно | Правило |
|-------|------|----------|------|
| `escalation_id` | string | yes | Формат идентификатора |
 `| session_id | string | yes | |`
| `Сессия_id` | строка | да | |

| `Сессия_id` | string | yes | |
| `Сессия_id` | строка | да | |

| `Сессия_id` | строка | да | |` (with proper formatting)
| `Сессия_id` | строка | да | |

| `session_id` | строка | да | |
| `raised_by_role` | строка | да | |
| `reason` | enum | yes | `эскалация_причина` |
ности` (typo in thought, fix: `уровень_серьёзности`).
| `уровень_серьёзности` | enum | yes | |


 [Output]: `| `уровень_серьёзности` | enum | yes | |` (with proper formatting)
| `уровень_серьёзности` | enum | yes | |
 [Output] `| `уровень_серьёзности` | enum | yes | |`
| `уровень_серьёзности` | enum | yes | |

| `blocker` | строка | да | 1–2000 символов |


| `positions` | object[] | да | `{role_id, позиция, summary}` на сторону |

 | `positions` | object[] | да | `{Роль_id, позиция, summary}` на сторону |

 `One concrete decision or missing input` -> `Одно конкретное решение или отсутствующие входные данные` / `Конкретное решение или недостающие данные`

| `operator_request` | строка | да | Одно конкретное решение или отсутствующие входные данные |




| `fallback_strategy` | string | yes | Что произойдёт, если оператор не ответит |

| `timeout_at` | метка времени \| null | да | `null`, если срок не установлен |

`` `Резолюция` `` | объект | да | `{state: pending\|accepted\|rejected\|superseded\|expired, note, operator_id, resolved_at}` |

| `resume_Фаза` | integer | yes | Точная фаза для возобновления |

| `resume_Фаза` | integer | да | Точная фаза для возобновления |



| `resume_Фаза` | integer | да | Точная фаза для возобновления |` (or keep `yes` if preferred, but `да` is fine).

| `resume_Фаза` | integer | да | Точная фаза для возобновления |

| `resume_phase` | integer | да | Точная фаза для возобновления |
