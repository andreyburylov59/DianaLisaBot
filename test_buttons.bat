@echo off
chcp 65001 > nul
echo ========================================
echo АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ КНОПОК БОТА
echo ========================================
echo.
python test_all_buttons_auto.py
echo.
pause


