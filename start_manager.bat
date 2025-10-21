@echo off
chcp 65001 >nul
title DianaLisa Bot Manager

echo DianaLisa Bot Manager
echo ========================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверяем наличие файлов
if not exist "main.py" (
    echo Файл main.py не найден!
    pause
    exit /b 1
)

if not exist "bot_manager.py" (
    echo Файл bot_manager.py не найден!
    pause
    exit /b 1
)

REM Создаем директорию для логов
if not exist "logs" mkdir logs

echo Все файлы найдены
echo Запуск бота в фоновом режиме...
echo.

REM Запускаем менеджер бота в фоне
start /min "" python bot_manager.py

echo Bot Manager запущен в фоновом режиме
echo Логи сохраняются в папке logs/
echo Для остановки закройте это окно
echo.

REM Ждем немного и показываем статус
timeout /t 3 /nobreak >nul

echo Статус процессов:
tasklist /fi "imagename eq python.exe" /fo table | findstr python

echo.
echo Совет: Оставьте это окно открытым для мониторинга
echo Для полной остановки закройте это окно
echo.

pause
