"""Доступ к данным заказов: оформление, просмотр, редактирование, удаление.

Каждая операция изменения выполняется в одной транзакции и одновременно
пересчитывает доступное количество товарных позиций (stock_items).
"""
from datetime import date

from app.db import DatabaseError, fetch_all, fetch_one, transaction


class OrderError(Exception):
    """Ошибка бизнес-логики заказа (например, товара не хватает)."""


def get_orders():
    """Список заказов: номер, дата, ФИО клиента, кол-во пар и итоговая сумма."""
    return fetch_all(
        """
        SELECT o.order_id,
               o.order_date,
               u.last_name, u.first_name, u.middle_name,
               COALESCE(SUM(oi.quantity), 0) AS total_pairs,
               COALESCE(SUM(oi.quantity * oi.price), 0) AS total_sum
        FROM orders o
        JOIN users u ON u.user_id = o.user_id
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY o.order_id, u.user_id
        ORDER BY o.order_date DESC, o.order_id DESC
        """
    )


def get_order(order_id):
    return fetch_one(
        """
        SELECT o.order_id, o.order_date, u.last_name, u.first_name, u.middle_name
        FROM orders o
        JOIN users u ON u.user_id = o.user_id
        WHERE o.order_id = %s
        """,
        (order_id,),
    )


def get_order_items(order_id):
    """Состав заказа: модель (наименование + производство), размер, количество, цена."""
    return fetch_all(
        """
        SELECT oi.order_item_id,
               p.product_name,
               m.manufacturer_name,
               z.size_value,
               oi.quantity,
               oi.price,
               oi.quantity * oi.price AS line_sum
        FROM order_items oi
        JOIN stock_items s ON s.stock_item_id = oi.stock_item_id
        JOIN products p ON p.product_id = s.product_id
        JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
        JOIN sizes z ON z.size_id = s.size_id
        WHERE oi.order_id = %s
        ORDER BY oi.order_item_id
        """,
        (order_id,),
    )


def create_order(user_id, items, order_date=None):
    """Оформляет заказ. items — список словарей stock_item_id/quantity/price.

    Возвращает номер созданного заказа.
    """
    if not items:
        raise OrderError("Заказ пуст: добавьте хотя бы одну товарную позицию.")
    order_date = order_date or date.today()
    with transaction() as cursor:
        for item in items:
            # FOR UPDATE блокирует строку остатка до конца транзакции,
            # чтобы два одновременных заказа не продали одну и ту же пару.
            cursor.execute(
                "SELECT quantity_available FROM stock_items WHERE stock_item_id = %s FOR UPDATE",
                (item["stock_item_id"],),
            )
            row = cursor.fetchone()
            available = row["quantity_available"] if row else 0
            if item["quantity"] > available:
                raise OrderError(
                    "Позиции «{}», размер {} осталось только {} шт., а в заказе {} шт.\n"
                    "Уменьшите количество или удалите позицию из заказа.".format(
                        item["product_name"], item["size_text"], available, item["quantity"]
                    )
                )
        cursor.execute(
            "INSERT INTO orders (order_date, user_id) VALUES (%s, %s) RETURNING order_id",
            (order_date, user_id),
        )
        order_id = cursor.fetchone()["order_id"]
        for item in items:
            cursor.execute(
                "INSERT INTO order_items (order_id, stock_item_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item["stock_item_id"], item["quantity"], item["price"]),
            )
            cursor.execute(
                "UPDATE stock_items SET quantity_available = quantity_available - %s WHERE stock_item_id = %s",
                (item["quantity"], item["stock_item_id"]),
            )
    return order_id


def _return_items_to_stock(cursor, order_id, order_item_ids=None):
    """Возвращает на склад пары из позиций заказа (всех или перечисленных)."""
    query = """
        UPDATE stock_items s
        SET quantity_available = s.quantity_available + oi.quantity
        FROM order_items oi
        WHERE oi.stock_item_id = s.stock_item_id AND oi.order_id = %s
    """
    params = [order_id]
    if order_item_ids is not None:
        query += " AND oi.order_item_id = ANY(%s)"
        params.append(list(order_item_ids))
    cursor.execute(query, params)


def delete_order(order_id):
    """Удаляет заказ вместе с составом (ON DELETE CASCADE) и возвращает пары на склад."""
    with transaction() as cursor:
        cursor.execute("SELECT 1 FROM orders WHERE order_id = %s FOR UPDATE", (order_id,))
        if cursor.fetchone() is None:
            raise OrderError("Заказ №{} не найден — возможно, его уже удалил другой пользователь.".format(order_id))
        _return_items_to_stock(cursor, order_id)
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))


def update_order(order_id, order_date, removed_item_ids):
    """Редактирование заказа администратором: дата и удаление позиций."""
    removed_item_ids = list(removed_item_ids)
    with transaction() as cursor:
        cursor.execute("SELECT COUNT(*) AS item_count FROM order_items WHERE order_id = %s", (order_id,))
        if cursor.fetchone()["item_count"] <= len(removed_item_ids):
            raise OrderError(
                "В заказе должна остаться хотя бы одна позиция.\n"
                "Чтобы убрать все позиции, удалите заказ целиком в списке заказов."
            )
        cursor.execute("UPDATE orders SET order_date = %s WHERE order_id = %s", (order_date, order_id))
        if removed_item_ids:
            _return_items_to_stock(cursor, order_id, removed_item_ids)
            cursor.execute(
                "DELETE FROM order_items WHERE order_id = %s AND order_item_id = ANY(%s)",
                (order_id, removed_item_ids),
            )


__all__ = [
    "DatabaseError", "OrderError", "get_orders", "get_order", "get_order_items",
    "create_order", "delete_order", "update_order",
]
