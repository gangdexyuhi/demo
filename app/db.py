"""Подключение к базе данных PostgreSQL."""
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG


class DatabaseError(Exception):
    """Ошибка работы с базой, текст которой можно показать пользователю."""


def get_connection():
    try:
        # RealDictCursor возвращает строки как словари: row["product_name"]
        return psycopg2.connect(cursor_factory=RealDictCursor, connect_timeout=5, **DB_CONFIG)
    except psycopg2.OperationalError as error:
        raise DatabaseError(
            "Не удалось подключиться к базе данных «{}» на {}:{}.\n"
            "Проверьте, что сервер PostgreSQL запущен, база создана, "
            "а логин и пароль в файле config.py указаны верно.\n\n"
            "Подробности: {}".format(DB_CONFIG["dbname"], DB_CONFIG["host"], DB_CONFIG["port"], error)
        )


@contextmanager
def transaction():
    """Курсор внутри транзакции: commit при успехе, rollback при ошибке."""
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                yield cursor
    except psycopg2.Error as error:
        raise DatabaseError("Ошибка при работе с базой данных:\n{}".format(error)) from error
    finally:
        connection.close()


def fetch_all(query, params=None):
    with transaction() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(query, params=None):
    with transaction() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()
