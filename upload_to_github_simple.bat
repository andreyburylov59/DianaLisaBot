@echo off
chcp 65001 > nul
echo =========================================
echo ЗАГРУЗКА НА GITHUB
echo =========================================
echo.

git init
git add .
git commit -m "Начальная версия с CI/CD"
git branch -M main
git remote add origin https://github.com/andreyburylov59/DianaLisaBot.git
git push -u origin main

echo.
echo =========================================
echo ГОТОВО!
echo =========================================
echo.
echo Теперь зайдите на:
echo https://github.com/andreyburylov59/DianaLisaBot
echo.
echo И нажмите вкладку "Actions"
echo.
pause


