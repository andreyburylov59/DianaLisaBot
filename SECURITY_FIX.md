# 🚨 СРОЧНОЕ ИСПРАВЛЕНИЕ БЕЗОПАСНОСТИ

## ⚠️ Проблема
GitHub обнаружил ваш токен Telegram-бота в коде! Это критическая уязвимость безопасности.

## 🔧 Шаги для исправления

### 1. Отзовите старый токен (НЕМЕДЛЕННО!)

1. Откройте Telegram
2. Найдите бота **@BotFather**
3. Отправьте команду: `/revoke`
4. Выберите вашего бота из списка
5. Подтвердите отзыв
6. **ПОЛУЧИТЕ НОВЫЙ ТОКЕН** командой `/token`

### 2. Создайте файл .env

В папке проекта создайте файл `.env` (он уже в `.gitignore`):

```env
# 🤖 Telegram Bot Token
BOT_TOKEN=ваш_новый_токен_от_BotFather

# 👤 Ваш Telegram ID (узнать у @userinfobot)
ADMIN_IDS=260916055

# 💰 Платежный токен (опционально)
PAYMENT_PROVIDER_TOKEN=

# 🗄️ База данных
DATABASE_PATH=dianalisa_bot.db
```

### 3. Удалите токен из истории Git

Токен уже попал в историю Git на GitHub. Выполните:

```bash
# Удаляем файл config.py из истории Git
git filter-repo --path config.py --invert-paths

# Или используйте BFG Repo-Cleaner (проще)
# Скачайте с https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --replace-text passwords.txt
```

**passwords.txt** должен содержать:
```
8470739086:AAE0od-IRnEmzBF_8RMFOJqUNsvUYKlgnZM
```

### 4. Закройте предупреждение на GitHub

1. Перейдите: https://github.com/andreyburylov59/DianaLisaBot/security
2. Откройте предупреждение о токене
3. Нажмите "Close as revoked" (Закрыть как отозванное)

### 5. Проверьте другие секреты

Убедитесь, что в коде нет других секретов:

```bash
# Поиск возможных токенов
grep -r "AAE\|TOKEN\|API_KEY\|SECRET" --include="*.py" .
```

## ✅ Проверка

После всех шагов:

1. ✅ Старый токен отозван в @BotFather
2. ✅ Новый токен добавлен в `.env`
3. ✅ Файл `.env` НЕ в Git (проверка: `git status`)
4. ✅ Бот работает с новым токеном
5. ✅ Предупреждение на GitHub закрыто

## 🛡️ Правила безопасности на будущее

1. **НИКОГДА** не коммитьте файлы `.env`
2. **ВСЕГДА** используйте `os.getenv()` для секретов
3. **ПРОВЕРЯЙТЕ** `.gitignore` перед коммитом
4. **ИСПОЛЬЗУЙТЕ** GitHub Secrets для CI/CD
5. **РЕВЬЮ** код перед push на GitHub

## 📞 Помощь

Если что-то не получается - пишите!

