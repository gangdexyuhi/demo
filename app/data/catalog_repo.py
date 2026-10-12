"""Доступ к данным каталога: модели обуви, категории, товарные позиции."""
from app.db import fetch_all, fetch_one
from app.discount import calculate_discounted_price, get_previous_month_range

# Общая часть запроса: модель + суммарное количество по всем размерам +
# признак «были заказы за прошлый месяц» (нужен для расчёта скидки).
PRODUCTS_QUERY = """
    SELECT p.product_id,
           p.product_name,
           p.subcategory,
           p.description,
           p.composition,
           p.price,
           p.image_path,
           c.category_id,
           c.category_name,
           m.manufacturer_name,
           COALESCE((SELECT SUM(s.quantity_available)
                     FROM stock_items s
                     WHERE s.product_id = p.product_id), 0) AS total_quantity,
           EXISTS (SELECT 1
                   FROM order_items oi
                   JOIN stock_items s ON s.stock_item_id = oi.stock_item_id
                   JOIN orders o ON o.order_id = oi.order_id
                   WHERE s.product_id = p.product_id
                     AND o.order_date >= %(month_start)s
                     AND o.order_date < %(month_end)s) AS has_orders_last_month
    FROM products p
    JOIN categories c ON c.category_id = p.category_id
    JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
"""

SORT_NONE = 0
SORT_PRICE_ASC = 1
SORT_PRICE_DESC = 2


def _with_final_price(product):
    product["final_price"] = calculate_discounted_price(product["price"], product["has_orders_last_month"])
    product["has_discount"] = product["final_price"] < product["price"]
    return product


def get_categories():
    return fetch_all("SELECT category_id, category_name FROM categories ORDER BY category_name")


def get_products(search_text="", category_id=None, sort_mode=SORT_NONE, calculation_date=None):
    """Каталог с учётом поиска, фильтра по категории и сортировки по цене.

    Порядок как в ТЗ: фильтр по категории -> поиск -> сортировка результата.
    """
    month_start, month_end = get_previous_month_range(calculation_date)
    params = {"month_start": month_start, "month_end": month_end, "category_id": category_id}
    query = PRODUCTS_QUERY
    if category_id is not None:
        query += " WHERE p.category_id = %(category_id)s"
    query += " ORDER BY p.product_id"
    products = [_with_final_price(row) for row in fetch_all(query, params)]

    # Поиск без учёта регистра выполняем в Python: casefold() корректно
    # работает с кириллицей независимо от локали, в которой создана база.
    search_text = (search_text or "").strip().casefold()
    if search_text:
        products = [
            product for product in products
            if search_text in (product["product_name"] or "").casefold()
            or search_text in (product["description"] or "").casefold()
        ]

    # Сортируем по цене со скидкой — именно её видит пользователь.
    if sort_mode == SORT_PRICE_ASC:
        products.sort(key=lambda product: product["final_price"])
    elif sort_mode == SORT_PRICE_DESC:
        products.sort(key=lambda product: product["final_price"], reverse=True)
    return products


def get_product(product_id, calculation_date=None):
    month_start, month_end = get_previous_month_range(calculation_date)
    params = {"month_start": month_start, "month_end": month_end, "product_id": product_id}
    row = fetch_one(PRODUCTS_QUERY + " WHERE p.product_id = %(product_id)s", params)
    return _with_final_price(row) if row else None


def get_stock_items(product_id):
    """Размерный ряд модели: все размеры с доступным количеством (в т.ч. 0)."""
    return fetch_all(
        """
        SELECT s.stock_item_id, z.size_value, s.quantity_available
        FROM stock_items s
        JOIN sizes z ON z.size_id = s.size_id
        WHERE s.product_id = %s
        ORDER BY z.size_value
        """,
        (product_id,),
    )


def format_size(size_value):
    """Decimal('36.0') -> '36', Decimal('36.5') -> '36.5'"""
    return "{:g}".format(float(size_value))
