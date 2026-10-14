-- =====================================================================
-- «Чудо Обувь» — структура базы данных системы оформления заказа обуви
-- СУБД: PostgreSQL
-- Запуск: в pgAdmin откройте Query Tool на базе chudo_obuv и выполните
-- весь скрипт (F5) либо: psql -U postgres -d chudo_obuv -f schema.sql
-- =====================================================================

-- Удаляем в обратном порядке зависимостей, чтобы скрипт можно было
-- выполнять повторно.
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stock_items CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sizes CASCADE;
DROP TABLE IF EXISTS manufacturers CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- ===== Справочники =====

CREATE TABLE roles (
    role_id     SERIAL PRIMARY KEY,
    role_name   VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id     SERIAL PRIMARY KEY,
    manufacturer_name   VARCHAR(150) NOT NULL UNIQUE
);

-- Размер хранится числом: в данных есть половинные размеры (36.5, 37.5 ...)
CREATE TABLE sizes (
    size_id     SERIAL PRIMARY KEY,
    size_value  NUMERIC(4, 1) NOT NULL UNIQUE CHECK (size_value > 0)
);

-- ===== Основные таблицы =====

-- Гость (неавторизованный пользователь) в базе не хранится
CREATE TABLE users (
    user_id     SERIAL PRIMARY KEY,
    last_name   VARCHAR(100) NOT NULL,
    first_name  VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login       VARCHAR(50)  NOT NULL UNIQUE,
    role_id     INTEGER NOT NULL REFERENCES roles (role_id) ON DELETE RESTRICT
);

-- Модель обуви
CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES categories (category_id) ON DELETE RESTRICT,
    subcategory     VARCHAR(100),
    product_name    VARCHAR(255) NOT NULL,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers (manufacturer_id) ON DELETE RESTRICT,
    image_path      VARCHAR(255),
    description     TEXT,
    composition     TEXT,
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    UNIQUE (product_name, manufacturer_id)
);

-- Товарная позиция: сочетание модели и размера + доступное количество
CREATE TABLE stock_items (
    stock_item_id       SERIAL PRIMARY KEY,
    product_id          INTEGER NOT NULL REFERENCES products (product_id) ON DELETE CASCADE,
    size_id             INTEGER NOT NULL REFERENCES sizes (size_id) ON DELETE RESTRICT,
    quantity_available  INTEGER NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
    UNIQUE (product_id, size_id)
);

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    order_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id     INTEGER NOT NULL REFERENCES users (user_id) ON DELETE RESTRICT
);

-- Состав заказа: цена фиксируется на момент оформления заказа.
-- При удалении заказа его позиции удаляются вместе с ним (CASCADE),
-- а товарную позицию, которая есть в заказах, удалить нельзя (RESTRICT).
CREATE TABLE order_items (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    stock_item_id   INTEGER NOT NULL REFERENCES stock_items (stock_item_id) ON DELETE RESTRICT,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
);

CREATE INDEX ix_orders_user_id ON orders (user_id);
CREATE INDEX ix_order_items_order_id ON order_items (order_id);
CREATE INDEX ix_stock_items_product_id ON stock_items (product_id);
