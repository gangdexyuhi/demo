#!/bin/sh
# Сборка исполняемого файла для Linux (запускать из корня проекта в активированном venv)
pyinstaller --noconfirm --onefile --name ChudoObuv \
  --add-data "resources:resources" \
  --exclude-module PyQt5 \
  main.py
echo "Готово: dist/ChudoObuv"
