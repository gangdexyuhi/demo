"""Модуль 5 — шаблон расчётов по данным Приложения 4 (pandas).

ВНИМАНИЕ: файлов Приложения 4 в материалах курса нет, поэтому названия колонок
ниже взяты из текста задания и могут отличаться. Перед запуском:
    1. положите CSV рядом со скриптом;
    2. выполните show_columns() и поправьте константы в блоке «Колонки».

Запуск: pip install pandas  ->  python module5_analysis.py
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

# ---------- Колонки (сверить с файлами!) ----------
USER_ID = "user_id"
SESSION_ID = "session_id"
SESSION_START = "session_start"      # время начала сессии
DEVICE_TYPE = "device_type"
TRAFFIC_SOURCE = "traffic_source"
ORDER_ID = "order_id"
ORDER_DATE = "order_date"            # время оформления заказа
STATUS = "status"
COMPLETED = "completed"
MODEL_ID = "model_id"
PRICE = "price"
QUANTITY = "quantity"
DISCOUNT = "discount_percent"
CATEGORY = "category"

PERIOD_START = "2026-01-01"
PERIOD_END = "2026-04-01"            # правая граница не включается (до 31.03 включительно)


def load(name):
    return pd.read_csv(DATA_DIR / name, encoding="utf-8")


def show_columns():
    for name in ("Sessions_analytics.csv", "Orders_analytics.csv",
                 "Order_items_analytics.csv", "Shoe_models_analytics.csv"):
        print(name, list(load(name).columns))


def load_data():
    sessions = load("Sessions_analytics.csv")
    orders = load("Orders_analytics.csv")
    items = load("Order_items_analytics.csv")
    models = load("Shoe_models_analytics.csv")
    sessions[SESSION_START] = pd.to_datetime(sessions[SESSION_START])
    orders[ORDER_DATE] = pd.to_datetime(orders[ORDER_DATE])
    in_period = (orders[ORDER_DATE] >= PERIOD_START) & (orders[ORDER_DATE] < PERIOD_END)
    completed = orders[in_period & (orders[STATUS].str.lower() == COMPLETED)]
    return sessions, orders, completed, items, models


def task_5_1(sessions, completed):
    """Конверсия по device_type = покупатели / посетители (уникальные пользователи)."""
    visitors = sessions.groupby(DEVICE_TYPE)[USER_ID].nunique()
    # тип устройства покупки — по сессии, связанной с заказом
    buyers = completed.merge(sessions[[SESSION_ID, DEVICE_TYPE]], on=SESSION_ID)
    buyers = buyers.groupby(DEVICE_TYPE)[USER_ID].nunique()
    conversion = (buyers / visitors).fillna(0)
    print("5.1 конверсия:\n", conversion.round(4))
    return conversion.idxmax()


def task_5_2(sessions, completed):
    """Медиана минут от первой сессии до первой завершённой покупки (<= 7 суток)."""
    first_visit = sessions.groupby(USER_ID)[SESSION_START].min()
    first_order = completed.groupby(USER_ID)[ORDER_DATE].min()
    delta = (first_order - first_visit).dropna()
    delta = delta[(delta >= pd.Timedelta(0)) & (delta <= pd.Timedelta(days=7))]
    return round(delta.dt.total_seconds().median() / 60, 2)


def task_5_3(sessions):
    """Удержание в феврале пользователей, впервые пришедших в январе, по каналу первой сессии."""
    first = sessions.sort_values(SESSION_START).groupby(USER_ID).first()
    january_users = first[(first[SESSION_START] >= "2026-01-01") & (first[SESSION_START] < "2026-02-01")]
    february = sessions[(sessions[SESSION_START] >= "2026-02-01") & (sessions[SESSION_START] < "2026-03-01")]
    returned = set(february[USER_ID])
    retention = january_users.groupby(TRAFFIC_SOURCE).apply(
        lambda group: group.index.isin(returned).mean()
    )
    print("5.3 удержание:\n", retention.round(4))
    return retention.idxmax()


def task_5_4(completed, items):
    """Число заказов после удаления выбросов по правилу 1,5 IQR."""
    lines = items[items[ORDER_ID].isin(completed[ORDER_ID])].copy()
    lines["line_sum"] = lines[PRICE] * lines[QUANTITY]
    order_sum = lines.groupby(ORDER_ID)["line_sum"].sum()
    q1, q3 = order_sum.quantile(0.25), order_sum.quantile(0.75)
    iqr = q3 - q1
    kept = order_sum[(order_sum >= q1 - 1.5 * iqr) & (order_sum <= q3 + 1.5 * iqr)]
    return len(kept)


def task_5_5(completed, items):
    """Корреляция Пирсона между discount_percent и quantity (3 знака)."""
    lines = items[items[ORDER_ID].isin(completed[ORDER_ID])]
    # discount_percent может лежать в заказах, а не в позициях — тогда сделать merge
    if DISCOUNT not in lines.columns:
        lines = lines.merge(completed[[ORDER_ID, DISCOUNT]], on=ORDER_ID)
    return round(lines[DISCOUNT].corr(lines[QUANTITY]), 3)


def task_5_6(completed, items, models):
    """Категория с максимальным числом проданных пар."""
    lines = items[items[ORDER_ID].isin(completed[ORDER_ID])].merge(models[[MODEL_ID, CATEGORY]], on=MODEL_ID)
    totals = lines.groupby(CATEGORY)[QUANTITY].sum()
    print("5.6 пары по категориям:\n", totals)
    return totals.idxmax()


def main():
    show_columns()
    sessions, _orders, completed, items, models = load_data()
    print("5.1:", task_5_1(sessions, completed))
    print("5.2:", task_5_2(sessions, completed))
    print("5.3:", task_5_3(sessions))
    print("5.4:", task_5_4(completed, items))
    print("5.5:", task_5_5(completed, items))
    print("5.6:", task_5_6(completed, items, models))


if __name__ == "__main__":
    main()
