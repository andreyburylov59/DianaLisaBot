# План рефакторинга callbacks.py

## ⚠️ ВАЖНО: Не начинать без полного тестирования!

Файл `callbacks.py` имеет 1945 строк и содержит 71 обработчик.
Полное разделение требует осторожности, чтобы не сломать работающий код.

## 📊 Текущая структура

### Обработчики по категориям:

#### 1. Главное меню и навигация (10 handlers)
- `handle_main_menu`
- `handle_faq`
- `handle_contact_support`
- `handle_back_to_registration_start`
- Итого: ~300 строк

#### 2. Тренировки (15 handlers)
- `handle_start_training`
- `handle_training_day_1/2/3`
- `handle_mark_training`
- `handle_training_feedback`
- `handle_difficulty_rating`
- `handle_clarity_rating`
- `handle_finish_feedback`
- `handle_skip_feedback`
- `handle_view_results`
- Итого: ~500 строк

#### 3. Обратная связь (4 handlers)
- `handle_feedback_like`
- `handle_feedback_dislike`
- `log_feedback`
- `schedule_next_day_opening`
- `open_next_training_day`
- Итого: ~200 строк

#### 4. Платежи (6 handlers)
- `handle_buy_course`
- `handle_buy_training`
- `handle_package_selection`
- `handle_package_basic`
- `handle_training_selection`
- `handle_training_single/pack5/pack10/unlimited`
- `handle_payment_success`
- `handle_payment_cancel`
- Итого: ~150 строк

#### 5. Админ-панель (15 handlers)
- `handle_admin_action`
- `handle_admin_command`
- `handle_admin_stats`
- `handle_admin_users`
- `handle_admin_payments`
- `handle_admin_reviews`
- `handle_admin_training_feedback`
- `handle_admin_analytics`
- `handle_admin_export_db`
- `handle_admin_send_message`
- `handle_admin_menu`
- `handle_admin_clear_db`
- `handle_confirm_clear_db`
- `handle_confirm_broadcast`
- `handle_cancel_broadcast`
- Итого: ~600 строк

#### 6. Регистрация и настройки (12 handlers)
- `handle_start_registration`
- `handle_skip_phone`
- `handle_timezone_selection`
- `handle_timezone_moscow/kiev/minsk` и др.
- Итого: ~200 строк

#### 7. Вспомогательные (9 handlers)
- `handle_rating_1/2/3/4/5`
- `handle_yes/no`
- `handle_confirm/cancel`
- `handle_pagination`
- `handle_noop`
- `handle_leave_review`
- Итого: ~100 строк

## 🎯 План разделения (БУДУЩЕЕ)

### Этап 1: Подготовка
- [x] Создать директорию `callbacks_modules/`
- [x] Создать базовый класс `BaseCallbackHandler`
- [x] Создать резервную копию `callbacks_backup.py`
- [ ] Запустить все тесты перед изменениями

### Этап 2: Создание модулей (НЕ ВЫПОЛНЯТЬ БЕЗ ТЕСТОВ!)
- [ ] `callbacks_modules/training.py` - тренировки
- [ ] `callbacks_modules/feedback.py` - обратная связь
- [ ] `callbacks_modules/payment.py` - платежи
- [ ] `callbacks_modules/admin.py` - админ-панель
- [ ] `callbacks_modules/registration.py` - регистрация
- [ ] `callbacks_modules/navigation.py` - навигация

### Этап 3: Миграция (ОСТОРОЖНО!)
- [ ] Перенести методы по одному
- [ ] После каждого переноса запускать тесты
- [ ] Если тесты не проходят - ОТКАТИТЬ!

### Этап 4: Интеграция
- [ ] Обновить `callbacks.py` для импорта модулей
- [ ] Создать агрегирующий класс
- [ ] Обновить callback_map

### Этап 5: Тестирование
- [ ] Запустить все тесты
- [ ] Тестировать вручную
- [ ] Проверить логи на ошибки

## ⚠️ РИСКИ

1. **Высокий риск поломки** - код сильно связан
2. **Сложность импортов** - циклические зависимости
3. **Много времени** - требует тщательного тестирования
4. **Потенциальные баги** - могут появиться новые ошибки

## 💡 АЛЬТЕРНАТИВА (РЕКОМЕНДУЕТСЯ)

Вместо полного разделения:

### Вариант A: Комментарии и секции
```python
# ============================================================================
# ТРЕНИРОВКИ
# ============================================================================

async def handle_start_training(...):
    ...

# ============================================================================
# ОБРАТНАЯ СВЯЗЬ
# ============================================================================

async def handle_feedback_like(...):
    ...
```

### Вариант B: Вспомогательные функции в отдельных файлах
- `training_helpers.py` - вспомогательные функции для тренировок
- `payment_helpers.py` - вспомогательные функции для платежей
- Основной `callbacks.py` остается как есть

### Вариант C: Декомпозиция сложных методов
- Разбить большие методы (>100 строк) на мелкие
- Вынести повторяющийся код в утилиты
- Улучшить читаемость без изменения структуры

## 🎯 РЕКОМЕНДАЦИЯ

**НЕ ВЫПОЛНЯТЬ** полное разделение сейчас.

**ВМЕСТО ЭТОГО:**
1. Добавить комментарии-разделители в `callbacks.py`
2. Вынести вспомогательные функции в helpers
3. Улучшить документацию методов
4. Запланировать полный рефакторинг на будущее (когда будет 100% покрытие тестами)

## 📝 Статус

- **Текущий:** Создана структура модулей, НО НЕ ИСПОЛЬЗУЕТСЯ
- **Причина:** Риск поломки рабочего кода
- **Решение:** Отложить до лучших времен
- **Дата решения:** 2025-10-21

---

**ВАЖНО:** Если когда-нибудь решите провести полный рефакторинг:
1. Убедитесь, что есть 100% покрытие тестами
2. Делайте это постепенно (по 1 модулю за раз)
3. После каждого шага - тестируйте
4. Держите `callbacks_backup.py` для отката


