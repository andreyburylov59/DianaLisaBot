@echo off
chcp 65001 > nul
echo =========================================
echo ЗАГРУЗКА КОДА НА GITHUB
echo =========================================
echo.
echo ВАЖНО: Сначала создайте репозиторий на GitHub!
echo 1. Зайдите на https://github.com
echo 2. Нажмите "New repository"
echo 3. Название: DianaLisaBot
echo 4. Тип: Public
echo 5. Скопируйте URL репозитория
echo.
pause
echo.

REM Инициализация git (если еще не сделано)
if not exist .git (
    echo [1/5] Инициализация git...
    git init
    echo ✓ Git инициализирован
) else (
    echo [1/5] Git уже инициализирован ✓
)
echo.

REM Добавление всех файлов
echo [2/5] Добавление файлов...
git add .
echo ✓ Файлы добавлены
echo.

REM Создание коммита
echo [3/5] Создание коммита...
git commit -m "Начальная версия с CI/CD автотестированием"
echo ✓ Коммит создан
echo.

REM Переименование ветки в main
echo [4/5] Установка ветки main...
git branch -M main
echo ✓ Ветка установлена
echo.

REM Добавление remote
echo [5/5] Добавление GitHub remote...
echo.
echo ВНИМАНИЕ! Введите URL вашего репозитория:
echo Пример: https://github.com/ВАШ_USERNAME/DianaLisaBot.git
echo.
set /p REPO_URL="URL репозитория: "

git remote add origin %REPO_URL%
if errorlevel 1 (
    echo.
    echo Возможно remote уже существует, обновляем...
    git remote set-url origin %REPO_URL%
)
echo ✓ Remote добавлен
echo.

REM Загрузка на GitHub
echo =========================================
echo ЗАГРУЖАЕМ КОД НА GITHUB...
echo =========================================
echo.
git push -u origin main
echo.

if errorlevel 1 (
    echo.
    echo =========================================
    echo ОШИБКА ЗАГРУЗКИ!
    echo =========================================
    echo.
    echo Возможные причины:
    echo 1. Неправильный URL репозитория
    echo 2. Нет доступа к GitHub
    echo 3. Нужна аутентификация
    echo.
    echo Решение:
    echo 1. Проверьте URL репозитория
    echo 2. Убедитесь что залогинены в GitHub
    echo 3. Возможно нужен Personal Access Token
    echo.
    pause
    exit /b 1
)

echo.
echo =========================================
echo ✅ УСПЕШНО ЗАГРУЖЕНО НА GITHUB!
echo =========================================
echo.
echo Теперь:
echo 1. Зайдите на https://github.com/ВАШ_USERNAME/DianaLisaBot
echo 2. Нажмите вкладку "Actions"
echo 3. Увидите запущенные тесты (подождите 3-5 минут)
echo 4. Дождитесь зеленой галочки ✓
echo.
echo ГОТОВО! CI/CD РАБОТАЕТ!
echo.
pause


