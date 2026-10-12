@echo off
chcp 65001 >nul
rem Сборка ChudoObuv.exe (запускать из корня проекта в активированном venv)
pyinstaller --noconfirm --noconsole --onefile --name ChudoObuv ^
  --icon "resources\icon.ico" ^
  --add-data "resources;resources" ^
  --exclude-module PyQt5 ^
  main.py
echo Готово: dist\ChudoObuv.exe
pause
