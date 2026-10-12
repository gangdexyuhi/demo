"""Алгоритм расчёта цены товара с учётом скидки.

Скидка 25 % действует на модели, на которые не было заказов
за предыдущий календарный месяц относительно даты расчёта.
"""
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

DISCOUNT_PERCENT = Decimal("25")


def get_previous_month_range(calculation_date=None):
    """Возвращает (первый день прошлого месяца, первый день текущего месяца).

    Правая граница не включается: order_date >= start AND order_date < end.
    Например, для 15.03.2026 -> (01.02.2026, 01.03.2026).
    """
    if calculation_date is None:
        calculation_date = date.today()
    current_month_start = calculation_date.replace(day=1)
    # Шаг на один день назад от 1-го числа всегда попадает в прошлый месяц,
    # в том числе при переходе через год (январь -> декабрь).
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    return previous_month_start, current_month_start


def calculate_discounted_price(price, has_orders_last_month):
    """Цена со скидкой в рублях, округлённая до копеек."""
    price = Decimal(str(price))
    if has_orders_last_month:
        return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    discounted = price * (Decimal("100") - DISCOUNT_PERCENT) / Decimal("100")
    return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_rub(amount):
    """1234.5 -> '1 234,50 ₽'"""
    text = "{:,.2f}".format(Decimal(str(amount))).replace(",", " ").replace(".", ",")
    return text + " ₽"


def pairs_text(count):
    """1 пара, 2 пары, 5 пар, 21 пара — согласование слова с числом."""
    count = int(count)
    if count % 10 == 1 and count % 100 != 11:
        word = "пара"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        word = "пары"
    else:
        word = "пар"
    return "{} {}".format(count, word)
