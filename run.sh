#!/bin/bash
# Запуск приложения «Чудо Обувь»:  bash run.sh
cd "$(dirname "$0")" || exit 1
source venv/bin/activate
python main.py
