"""Импорт данных заказчика (папка import/*.xlsx) в базу chudo_obuv.

Запуск из корня проекта:
    python database/import_data.py            # создать таблицы и загрузить всё
    python database/import_data.py --no-schema  # только загрузить данные

Порядок загрузки важен: сначала справочники, потом то, что на них ссылается.
"""
import argparse
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import openpyxl
import psycopg2

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from config import DB_CONFIG  # noqa: E402

IMPORT_DIR = PROJECT_DIR / "import"
SCHEMA_FILE = PROJECT_DIR / "database" / "schema.sql"


def clean_text(value):
    """Нормализует строку из Excel; пустую строку превращает в None.

    В файлах заказчика встречаются неразрывные пробелы (\xa0) и переводы
    строк в конце — из-за них одна и та же модель в разных файлах
    не совпадала бы по названию.
    """
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def to_size(value):
    """'36.5', 36.5 и 36 -> Decimal с одним знаком после запятой."""
    return Decimal(str(value).replace(",", ".").strip()).quantize(Decimal("0.1"))


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for date_format in ("%d.%m.%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    raise ValueError("Не удалось разобрать дату: {}".format(value))


def read_rows(file_name):
    """Строки первого листа без заголовка; полностью пустые строки пропускаются."""
    workbook = openpyxl.load_workbook(IMPORT_DIR / file_name, data_only=True)
    sheet = workbook.worksheets[0]
    rows = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if any(cell not in (None, "") for cell in row):
            rows.append(row)
    return rows


def get_or_create(cursor, table, id_column, name_column, value):
    """Возвращает id записи справочника, при необходимости создаёт её.

    Имена таблиц/колонок задаются только в коде, поэтому подстановка
    через format безопасна; само значение передаётся параметром.
    """
    cursor.execute(
        "INSERT INTO {0} ({2}) VALUES (%s) "
        "ON CONFLICT ({2}) DO UPDATE SET {2} = EXCLUDED.{2} "
        "RETURNING {1}".format(table, id_column, name_column),
        (value,),
    )
    return cursor.fetchone()[0]


def import_sizes(cursor):
    count = 0
    for row in read_rows("Sizes_import.xlsx"):
        cursor.execute(
            "INSERT INTO sizes (size_value) VALUES (%s) ON CONFLICT (size_value) DO NOTHING",
            (to_size(row[0]),),
        )
        count += 1
    print("Размеры: {}".format(count))


def import_products(cursor):
    count = 0
    for row in read_rows("Products_import.xlsx"):
        category, subcategory, image, name, manufacturer, description, composition, price = row[:8]
        category_id = get_or_create(cursor, "categories", "category_id", "category_name", clean_text(category))
        manufacturer_id = get_or_create(
            cursor, "manufacturers", "manufacturer_id", "manufacturer_name", clean_text(manufacturer)
        )
        cursor.execute(
            """
            INSERT INTO products (category_id, subcategory, product_name, manufacturer_id,
                                  image_path, description, composition, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_name, manufacturer_id) DO UPDATE
                SET category_id = EXCLUDED.category_id,
                    subcategory = EXCLUDED.subcategory,
                    image_path = EXCLUDED.image_path,
                    description = EXCLUDED.description,
                    composition = EXCLUDED.composition,
                    price = EXCLUDED.price
            """,
            (
                category_id,
                clean_text(subcategory),
                clean_text(name),
                manufacturer_id,
                clean_text(image),
                clean_text(description),
                clean_text(composition),
                Decimal(str(price)),
            ),
        )
        count += 1
    print("Модели обуви: {}".format(count))


def import_users(cursor):
    count = 0
    for row in read_rows("Users_import.xlsx"):
        last_name, first_name, middle_name, login, role_name = row[:5]
        role_id = get_or_create(cursor, "roles", "role_id", "role_name", clean_text(role_name))
        cursor.execute(
            """
            INSERT INTO users (last_name, first_name, middle_name, login, role_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (login) DO UPDATE
                SET last_name = EXCLUDED.last_name,
                    first_name = EXCLUDED.first_name,
                    middle_name = EXCLUDED.middle_name,
                    role_id = EXCLUDED.role_id
            """,
            (clean_text(last_name), clean_text(first_name), clean_text(middle_name), clean_text(login), role_id),
        )
        count += 1
    print("Пользователи: {}".format(count))


def find_product_id(cursor, product_name, manufacturer_name):
    """Ищет модель по наименованию и производителю.

    Сначала точное совпадение. Если его нет — единственная модель того же
    производителя, наименование которой начинается с указанного: в остатках
    и заказах встречаются сокращённые названия («Черные туфли в классическом
    стиле» вместо полного названия из каталога).
    """
    cursor.execute(
        """
        SELECT p.product_id, p.product_name = %(name)s AS is_exact
        FROM products p
        JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
        WHERE m.manufacturer_name = %(manufacturer)s
          AND (p.product_name = %(name)s OR p.product_name LIKE %(prefix)s)
        ORDER BY is_exact DESC
        """,
        {"name": product_name, "manufacturer": manufacturer_name, "prefix": product_name + " %"},
    )
    found = cursor.fetchall()
    if found and (found[0][1] or len(found) == 1):
        return found[0][0]
    return None  # модели нет или похожих несколько — однозначно выбрать нельзя


def import_stock_items(cursor):
    count = 0
    skipped = set()
    for row in read_rows("Stock_Items_import.xlsx"):
        product_name, manufacturer_name, size_value, quantity = row[:4]
        product_name = clean_text(product_name)
        manufacturer_name = clean_text(manufacturer_name)
        product_id = find_product_id(cursor, product_name, manufacturer_name)
        # Без модели позицию не сохранить (внешний ключ) — пропускаем с предупреждением
        if product_id is None:
            skipped.add("{} ({})".format(product_name, manufacturer_name))
            continue
        cursor.execute(
            "INSERT INTO sizes (size_value) VALUES (%s) ON CONFLICT (size_value) DO NOTHING",
            (to_size(size_value),),
        )
        cursor.execute("SELECT size_id FROM sizes WHERE size_value = %s", (to_size(size_value),))
        size_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO stock_items (product_id, size_id, quantity_available)
            VALUES (%s, %s, %s)
            ON CONFLICT (product_id, size_id) DO UPDATE
                SET quantity_available = EXCLUDED.quantity_available
            """,
            (product_id, size_id, int(quantity or 0)),
        )
        count += 1
    print("Товарные позиции: {}".format(count))
    for item in sorted(skipped):
        print("  [пропущено] нет модели в каталоге: {}".format(item))


def find_user_id(cursor, full_name):
    parts = clean_text(full_name).split()
    last_name = parts[0]
    first_name = parts[1] if len(parts) > 1 else ""
    middle_name = " ".join(parts[2:]) if len(parts) > 2 else None
    cursor.execute(
        """
        SELECT user_id FROM users
        WHERE last_name = %s AND first_name = %s
          AND COALESCE(middle_name, '') = COALESCE(%s, '')
        """,
        (last_name, first_name, middle_name),
    )
    found = cursor.fetchone()
    return found[0] if found else None


def import_orders(cursor):
    order_count = 0
    item_count = 0
    seen_orders = set()
    for row in read_rows("Orders_import.xlsx"):
        order_number, order_date, full_name = row[0], row[1], row[2]
        product_name, manufacturer_name, size_value, quantity, price = row[4:9]
        user_id = find_user_id(cursor, full_name)
        if user_id is None:
            print("  [пропущено] клиент не найден: {}".format(full_name))
            continue
        # Номер заказа из файла сохраняем как order_id, чтобы строки
        # одного заказа попали в один заказ.
        cursor.execute(
            """
            INSERT INTO orders (order_id, order_date, user_id) VALUES (%s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
            """,
            (int(order_number), to_date(order_date), user_id),
        )
        order_count += cursor.rowcount
        # При повторном импорте (--no-schema) состав заказа загружаем заново,
        # чтобы позиции не задвоились.
        if int(order_number) not in seen_orders:
            seen_orders.add(int(order_number))
            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (int(order_number),))
        product_id = find_product_id(cursor, clean_text(product_name), clean_text(manufacturer_name))
        cursor.execute(
            """
            SELECT s.stock_item_id
            FROM stock_items s
            JOIN sizes z ON z.size_id = s.size_id
            WHERE s.product_id = %s AND z.size_value = %s
            """,
            (product_id, to_size(size_value)),
        )
        stock_item = cursor.fetchone()
        if stock_item is None:
            print("  [пропущено] нет товарной позиции: {} {} р.{}".format(product_name, manufacturer_name, size_value))
            continue
        cursor.execute(
            "INSERT INTO order_items (order_id, stock_item_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (int(order_number), stock_item[0], int(quantity), Decimal(str(price))),
        )
        item_count += 1
    # Т.к. order_id вставлялись явно, двигаем последовательность дальше,
    # иначе новый заказ из приложения получит уже занятый номер.
    cursor.execute(
        "SELECT setval(pg_get_serial_sequence('orders', 'order_id'), COALESCE(MAX(order_id), 0) + 1, false) FROM orders"
    )
    print("Заказы: {}, позиции заказов: {}".format(order_count, item_count))


def main():
    parser = argparse.ArgumentParser(description="Импорт данных «Чудо Обувь»")
    parser.add_argument("--no-schema", action="store_true", help="не пересоздавать таблицы")
    args = parser.parse_args()

    try:
        connection = psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as error:
        print("Не удалось подключиться к базе: {}".format(error))
        print("Проверьте, что база {} создана и пароль в config.py верный.".format(DB_CONFIG["dbname"]))
        sys.exit(1)

    try:
        with connection:
            with connection.cursor() as cursor:
                if not args.no_schema:
                    cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
                    print("Таблицы созданы")
                import_sizes(cursor)
                import_products(cursor)
                import_users(cursor)
                import_stock_items(cursor)
                import_orders(cursor)
        print("Импорт завершён успешно")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
