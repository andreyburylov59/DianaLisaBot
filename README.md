# 🤖 DianaLisa Bot

Telegram-бот для тренировок и фитнес-программ с автоматическим тестированием и CI/CD.

---

## 🚀 Быстрый старт

### Для пользователей бота:
1. Найдите бота в Telegram: `@DianaLisaBot`
2. Нажмите `/start`
3. Следуйте инструкциям

### Для разработчиков:

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ваш-username/DianaLisaBot.git
cd DianaLisaBot

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env файл
BOT_TOKEN=ваш_токен_бота
PAYMENT_TOKEN=ваш_платежный_токен
DATABASE_PATH=dianalisa_bot.db

# 4. Запустить тесты
test_buttons.bat

# 5. Запустить бота
python bot_manager.py
```

---

## 📚 Документация

### 🆕 Начните здесь:
- **[QUICK_SUMMARY.md](QUICK_SUMMARY.md)** - Краткая сводка проекта
- **[DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)** - Правила разработки (ОБЯЗАТЕЛЬНО!)

### 🧪 Тестирование:
- **[TESTING_RECOMMENDATIONS.md](TESTING_RECOMMENDATIONS.md)** - Рекомендации по тестированию
- **[FINAL_REPORT.md](FINAL_REPORT.md)** - Отчет по выполненным задачам
- `test_buttons.bat` - Запуск основных тестов (20 тестов)
- `test_edge_cases.bat` - Запуск edge case тестов (10 тестов)
- `run_with_tests.bat` - Запуск перед изменениями кода

### 🚀 CI/CD (Автоматизация):
- **[CI_CD_SETUP_COMPLETE.md](CI_CD_SETUP_COMPLETE.md)** - ✅ ЧТО НАСТРОЕНО
- **[QUICK_CI_CD_START.md](QUICK_CI_CD_START.md)** - ⚡ Быстрый старт (5 минут)
- **[CI_CD_GUIDE.md](CI_CD_GUIDE.md)** - 📘 Полное руководство
- **[CI_CD_VISUAL_GUIDE.md](CI_CD_VISUAL_GUIDE.md)** - 🎨 Визуальное руководство

### 🔧 Разработка:
- **[CALLBACKS_REFACTORING_PLAN.md](CALLBACKS_REFACTORING_PLAN.md)** - План рефакторинга
- **[BUTTON_FIX_REPORT.md](BUTTON_FIX_REPORT.md)** - Отчет о исправлениях кнопок
- **[LOGGING_IMPROVEMENT_REPORT.md](LOGGING_IMPROVEMENT_REPORT.md)** - Улучшение логирования

### ⚙️ Настройка:
- **[PERMANENT_BOT_SETUP.md](PERMANENT_BOT_SETUP.md)** - Постоянная работа бота
- **[DianaLisaBot_MESSAGES_EDITOR.md](DianaLisaBot_MESSAGES_EDITOR.md)** - Редактирование сообщений

---

## 🏗️ Структура проекта

```
DianaLisaBot/
├─ 🤖 Основные файлы бота:
│  ├─ bot.py                    # Главный файл бота
│  ├─ bot_manager.py            # Менеджер запуска
│  ├─ callbacks.py              # Обработчики callback'ов (1945 строк)
│  ├─ keyboards.py              # Клавиатуры
│  ├─ database.py               # Работа с БД
│  ├─ config.py                 # Конфигурация
│  ├─ training.py               # Тренировки
│  ├─ payment.py                # Платежи
│  └─ registration.py           # Регистрация
│
├─ 🧪 Тестирование:
│  ├─ test_all_buttons_auto.py  # Основные тесты (20)
│  ├─ test_edge_cases.py        # Edge cases (10)
│  ├─ test_buttons.bat          # Запуск основных
│  ├─ test_edge_cases.bat       # Запуск edge cases
│  └─ run_with_tests.bat        # Запуск перед изменениями
│
├─ 🚀 CI/CD (Автоматизация):
│  └─ .github/workflows/
│     ├─ tests.yml              # Автотесты
│     ├─ deploy.yml             # Деплой
│     └─ code-quality.yml       # Качество кода
│
├─ 📊 База данных:
│  └─ dianalisa_bot.db          # SQLite БД
│
├─ 📝 Логи:
│  └─ logs/dianalisa_bot.log    # Логи бота
│
└─ 📚 Документация:
   ├─ README.md                 # Этот файл
   ├─ QUICK_SUMMARY.md          # Краткая сводка
   ├─ DEVELOPMENT_RULES.md      # Правила разработки
   ├─ TESTING_RECOMMENDATIONS.md # Рекомендации
   ├─ CI_CD_*.md                # CI/CD документация
   └─ *.md                      # Другие отчеты
```

---

## ✨ Особенности

### ✅ Функциональность:
- 🏋️ 3 дня бесплатных тренировок
- 📅 Планировщик тренировок
- 💬 Обратная связь
- 💳 Интеграция платежей
- 👤 Регистрация пользователей
- 🌍 Поддержка часовых поясов
- 📊 Админ-панель

### 🧪 Тестирование:
- ✅ 20 основных тестов (100% проходят)
- ✅ 10 edge case тестов (100% проходят)
- ✅ Автоматический запуск перед коммитом
- ✅ Покрытие всех кнопок и callback'ов

### 🚀 CI/CD:
- ✅ Автоматическое тестирование на GitHub
- ✅ Проверка качества кода
- ✅ Email уведомления
- ✅ Защита от деплоя сломанного кода
- ✅ Готовность к автодеплою

---

## 🛠️ Технологии

- **Python** 3.13
- **python-telegram-bot** - Telegram Bot API
- **SQLite** - База данных
- **APScheduler** - Планировщик задач
- **GitHub Actions** - CI/CD
- **pytz** - Часовые пояса

---

## 📋 Рабочий процесс

### 1. Разработка:
```bash
# Перед изменениями
run_with_tests.bat

# Вносите изменения
# ...

# После изменений
test_buttons.bat
test_edge_cases.bat

# Коммит
git add .
git commit -m "Описание изменений"
git push
```

### 2. Автоматическое тестирование:
```
GitHub Actions автоматически:
✅ Запускает все тесты
✅ Проверяет качество кода
✅ Отправляет уведомления
✅ Блокирует деплой если тесты не прошли
```

### 3. Деплой:
```
Если все тесты прошли:
✅ Готов к деплою
✅ Можно обновлять бота
```

---

## 📊 Статус проекта

![Tests](https://github.com/ваш-username/DianaLisaBot/workflows/Автоматическое%20тестирование%20бота/badge.svg)
![Deploy](https://github.com/ваш-username/DianaLisaBot/workflows/Автоматический%20деплой/badge.svg)

- **Основные тесты:** ✅ 20/20 (100%)
- **Edge case тесты:** ✅ 10/10 (100%)
- **Покрытие кода:** ~95%
- **Статус:** 🟢 PRODUCTION READY

---

## 🤝 Вклад в проект

### Правила:
1. **ОБЯЗАТЕЛЬНО** прочитайте [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)
2. **НИКОГДА** не удаляйте рабочий код
3. **ВСЕГДА** запускайте `run_with_tests.bat` перед изменениями
4. **ПРОВЕРЯЙТЕ** что все тесты проходят (100%)
5. **СОЗДАВАЙТЕ** pull request, не пушьте напрямую в main

### Процесс:
```bash
# 1. Создайте ветку
git checkout -b feature/новая-функция

# 2. Вносите изменения
# ...

# 3. Запустите тесты
run_with_tests.bat

# 4. Коммитите
git commit -m "Добавил новую функцию"

# 5. Создайте Pull Request
git push origin feature/новая-функция
```

---

## 🐛 Баг-репорты

Если нашли баг:
1. Проверьте что это не известная проблема
2. Создайте Issue на GitHub
3. Опишите как воспроизвести
4. Приложите логи если есть

---

## 📞 Контакты

- Telegram: `@your_username`
- Email: your@email.com
- GitHub Issues: [DianaLisaBot/issues](https://github.com/ваш-username/DianaLisaBot/issues)

---

## 📜 Лицензия

MIT License - свободное использование с указанием авторства.

---

## 🎯 Дорожная карта

### Ближайшие планы:
- [ ] Полный рефакторинг `callbacks.py`
- [ ] Добавить кэширование (Redis)
- [ ] Настроить автоматический деплой
- [ ] Добавить метрики и мониторинг
- [ ] Добавить больше тестов

### Долгосрочные:
- [ ] Веб-панель администратора
- [ ] API для мобильного приложения
- [ ] Интеграция с другими платформами
- [ ] Многоязычность

---

## 🙏 Благодарности

- Telegram Bot API
- Python community
- GitHub Actions
- Всем контрибьюторам

---

## 📈 Статистика

- **Строк кода:** ~5000+
- **Обработчиков callbacks:** 71
- **Тестов:** 30
- **Документации:** 13 файлов
- **Успешность тестов:** 100%

---

**Последнее обновление:** 2025-10-21  
**Версия:** 2.0  
**Статус:** 🟢 Production Ready


