"""Доступ к данным пользователей."""
from app.db import fetch_all, fetch_one

ROLE_ADMIN = "Администратор"
ROLE_MANAGER = "Менеджер"
ROLE_CLIENT = "Авторизованный пользователь"
ROLE_GUEST = "Гость"

USER_QUERY = """
    SELECT u.user_id, u.last_name, u.first_name, u.middle_name, u.login, r.role_name
    FROM users u
    JOIN roles r ON r.role_id = u.role_id
"""


def find_user_by_login(login):
    return fetch_one(USER_QUERY + " WHERE u.login = %s", (login,))


def get_users():
    return fetch_all(USER_QUERY + " ORDER BY u.last_name, u.first_name")


def make_guest():
    return {
        "user_id": None,
        "last_name": "Гость",
        "first_name": "",
        "middle_name": "",
        "login": "",
        "role_name": ROLE_GUEST,
    }


def full_name(user):
    parts = [user.get("last_name"), user.get("first_name"), user.get("middle_name")]
    return " ".join(part for part in parts if part)


def is_authorized(user):
    return user is not None and user.get("role_name") != ROLE_GUEST


def can_manage_orders(user):
    return user is not None and user.get("role_name") in (ROLE_ADMIN, ROLE_MANAGER)


def can_edit_orders(user):
    return user is not None and user.get("role_name") == ROLE_ADMIN
