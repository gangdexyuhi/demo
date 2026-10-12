"""Настройки подключения к базе данных PostgreSQL.

На экзамене поменяйте password на тот, что задавали при установке PostgreSQL.
Любой параметр можно переопределить переменной окружения (DB_HOST, DB_PASSWORD ...).
"""
import os

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ.get("DB_NAME", "chudo_obuv"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
}

APP_NAME = "Чудо Обувь"
