@echo off
rem Запуск эмулятора в Windows. Все аргументы передаются приложению.
cd /d "%~dp0"
python src\main.py %*
