--
-- PostgreSQL database dump
--


-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_role_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_items DROP CONSTRAINT IF EXISTS stock_items_size_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_items DROP CONSTRAINT IF EXISTS stock_items_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_manufacturer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.orders DROP CONSTRAINT IF EXISTS orders_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_stock_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_order_id_fkey;
DROP INDEX IF EXISTS public.ix_stock_items_product_id;
DROP INDEX IF EXISTS public.ix_orders_user_id;
DROP INDEX IF EXISTS public.ix_order_items_order_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_login_key;
ALTER TABLE IF EXISTS ONLY public.stock_items DROP CONSTRAINT IF EXISTS stock_items_product_id_size_id_key;
ALTER TABLE IF EXISTS ONLY public.stock_items DROP CONSTRAINT IF EXISTS stock_items_pkey;
ALTER TABLE IF EXISTS ONLY public.sizes DROP CONSTRAINT IF EXISTS sizes_size_value_key;
ALTER TABLE IF EXISTS ONLY public.sizes DROP CONSTRAINT IF EXISTS sizes_pkey;
ALTER TABLE IF EXISTS ONLY public.roles DROP CONSTRAINT IF EXISTS roles_role_name_key;
ALTER TABLE IF EXISTS ONLY public.roles DROP CONSTRAINT IF EXISTS roles_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_product_name_manufacturer_id_key;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE IF EXISTS ONLY public.orders DROP CONSTRAINT IF EXISTS orders_pkey;
ALTER TABLE IF EXISTS ONLY public.order_items DROP CONSTRAINT IF EXISTS order_items_pkey;
ALTER TABLE IF EXISTS ONLY public.manufacturers DROP CONSTRAINT IF EXISTS manufacturers_pkey;
ALTER TABLE IF EXISTS ONLY public.manufacturers DROP CONSTRAINT IF EXISTS manufacturers_manufacturer_name_key;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_category_name_key;
ALTER TABLE IF EXISTS public.users ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.stock_items ALTER COLUMN stock_item_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sizes ALTER COLUMN size_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.roles ALTER COLUMN role_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.products ALTER COLUMN product_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.orders ALTER COLUMN order_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.order_items ALTER COLUMN order_item_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.manufacturers ALTER COLUMN manufacturer_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN category_id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_user_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.stock_items_stock_item_id_seq;
DROP TABLE IF EXISTS public.stock_items;
DROP SEQUENCE IF EXISTS public.sizes_size_id_seq;
DROP TABLE IF EXISTS public.sizes;
DROP SEQUENCE IF EXISTS public.roles_role_id_seq;
DROP TABLE IF EXISTS public.roles;
DROP SEQUENCE IF EXISTS public.products_product_id_seq;
DROP TABLE IF EXISTS public.products;
DROP SEQUENCE IF EXISTS public.orders_order_id_seq;
DROP TABLE IF EXISTS public.orders;
DROP SEQUENCE IF EXISTS public.order_items_order_item_id_seq;
DROP TABLE IF EXISTS public.order_items;
DROP SEQUENCE IF EXISTS public.manufacturers_manufacturer_id_seq;
DROP TABLE IF EXISTS public.manufacturers;
DROP SEQUENCE IF EXISTS public.categories_category_id_seq;
DROP TABLE IF EXISTS public.categories;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    category_name character varying(100) NOT NULL
);


--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: manufacturers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.manufacturers (
    manufacturer_id integer NOT NULL,
    manufacturer_name character varying(150) NOT NULL
);


--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.manufacturers_manufacturer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.manufacturers_manufacturer_id_seq OWNED BY public.manufacturers.manufacturer_id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    order_item_id integer NOT NULL,
    order_id integer NOT NULL,
    stock_item_id integer NOT NULL,
    quantity integer NOT NULL,
    price numeric(10,2) NOT NULL,
    CONSTRAINT order_items_price_check CHECK ((price >= (0)::numeric)),
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0))
);


--
-- Name: order_items_order_item_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_items_order_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: order_items_order_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_items_order_item_id_seq OWNED BY public.order_items.order_item_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    order_date date DEFAULT CURRENT_DATE NOT NULL,
    user_id integer NOT NULL
);


--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    category_id integer NOT NULL,
    subcategory character varying(100),
    product_name character varying(255) NOT NULL,
    manufacturer_id integer NOT NULL,
    image_path character varying(255),
    description text,
    composition text,
    price numeric(10,2) NOT NULL,
    CONSTRAINT products_price_check CHECK ((price >= (0)::numeric))
);


--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL
);


--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;


--
-- Name: sizes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sizes (
    size_id integer NOT NULL,
    size_value numeric(4,1) NOT NULL,
    CONSTRAINT sizes_size_value_check CHECK ((size_value > (0)::numeric))
);


--
-- Name: sizes_size_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sizes_size_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sizes_size_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sizes_size_id_seq OWNED BY public.sizes.size_id;


--
-- Name: stock_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_items (
    stock_item_id integer NOT NULL,
    product_id integer NOT NULL,
    size_id integer NOT NULL,
    quantity_available integer DEFAULT 0 NOT NULL,
    CONSTRAINT stock_items_quantity_available_check CHECK ((quantity_available >= 0))
);


--
-- Name: stock_items_stock_item_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stock_items_stock_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stock_items_stock_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stock_items_stock_item_id_seq OWNED BY public.stock_items.stock_item_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    last_name character varying(100) NOT NULL,
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    login character varying(50) NOT NULL,
    role_id integer NOT NULL
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: manufacturers manufacturer_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manufacturers ALTER COLUMN manufacturer_id SET DEFAULT nextval('public.manufacturers_manufacturer_id_seq'::regclass);


--
-- Name: order_items order_item_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items ALTER COLUMN order_item_id SET DEFAULT nextval('public.order_items_order_item_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: roles role_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);


--
-- Name: sizes size_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sizes ALTER COLUMN size_id SET DEFAULT nextval('public.sizes_size_id_seq'::regclass);


--
-- Name: stock_items stock_item_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_items ALTER COLUMN stock_item_id SET DEFAULT nextval('public.stock_items_stock_item_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.categories (category_id, category_name) VALUES (1, 'Детская обувь');
INSERT INTO public.categories (category_id, category_name) VALUES (10, 'Женская обувь');
INSERT INTO public.categories (category_id, category_name) VALUES (23, 'Мужская обувь');


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (1, 'Малыш-Спорт');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (3, 'Лапушка');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (4, 'Тёплые ножки');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (5, 'Северята');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (6, 'Весна');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (7, 'Здоровый шаг');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (8, 'Карапуз');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (9, 'Маленький франт');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (12, 'Твой комфорт');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (15, 'Модный силуэт');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (13, 'Стиль и комфорт');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (23, 'Азимут');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (2, 'Топ-Топ');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (27, 'Берестов');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (14, 'Кожевенные традиции');
INSERT INTO public.manufacturers (manufacturer_id, manufacturer_name) VALUES (10, 'Барбари');


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (1, 1, 1, 1, 2190.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (2, 1, 20, 1, 2790.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (3, 2, 30, 1, 25000.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (4, 2, 39, 1, 7500.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (5, 3, 34, 1, 17000.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (6, 3, 57, 1, 8565.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (7, 3, 65, 1, 7795.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (8, 4, 50, 1, 7757.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (9, 4, 48, 1, 12340.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (10, 4, 44, 1, 7130.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (11, 4, 62, 1, 8765.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (12, 4, 32, 1, 15000.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (13, 5, 77, 1, 9567.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (14, 5, 87, 1, 21500.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (15, 5, 73, 1, 7890.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (16, 6, 80, 1, 24569.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (17, 6, 89, 1, 14567.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (18, 6, 91, 1, 15670.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (19, 7, 16, 1, 4290.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (20, 7, 2, 2, 2190.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (21, 7, 24, 1, 1690.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (22, 8, 86, 1, 25625.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (23, 8, 75, 3, 7890.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (24, 8, 70, 2, 6550.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (25, 9, 7, 1, 2490.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (26, 9, 14, 2, 3190.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (27, 10, 53, 1, 7550.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (28, 10, 43, 1, 7130.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (29, 10, 46, 1, 12340.00);
INSERT INTO public.order_items (order_item_id, order_id, stock_item_id, quantity, price) VALUES (30, 10, 61, 2, 8765.00);


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.orders (order_id, order_date, user_id) VALUES (1, '2026-04-02', 3);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (2, '2026-04-05', 17);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (3, '2026-04-08', 7);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (4, '2026-04-12', 15);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (5, '2026-04-18', 12);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (6, '2026-04-22', 9);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (7, '2026-04-25', 14);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (8, '2026-04-28', 20);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (9, '2026-05-05', 5);
INSERT INTO public.orders (order_id, order_date, user_id) VALUES (10, '2026-05-08', 17);


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (1, 1, 'Кроссовки', 'Кроссовки детские «Звёздочка» экокожа', 1, 'IMG_KS_195217.png', 'Кроссовки детские «Звёздочка» экокожа. Производитель: ООО «Малыш-Спорт», г. Смоленск', 'Верх — экокожа (полиуретан на хлопковой основе), подкладка — хлопок 100%, подошва — ПВХ', 2190.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (2, 1, 'Кроссовки', 'Кроссовки детские «Гонщик» экокожа', 2, 'IMG_KS_195213.png', 'Кроссовки детские «Гонщик» экокожа. Производитель: Фабрика «Топ-Топ», г. Киров', 'Верх — экокожа (микрофибра), подкладка — текстиль сетчатый (полиэстер), подошва — термопластичная резина (ТЭП)', 2490.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (3, 1, 'Кроссовки', 'Кроссовки детские «Радуга» экокожа перфорированная', 3, 'IMG_KS_195222.png', 'Кроссовки детские «Радуга» экокожа перфорированная. Производитель: ИП Смирнова Л.В. (бренд «Лапушка»), г. Вологда', 'Верх — экокожа перфорированная, вставки — нейлон, стелька — ортопедическая с латексной подушкой, подошва — ЭВА', 1990.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (4, 1, 'Сапоги', 'Сапожки детские «Снежинка» зимние на меху', 4, 'IMG_KB_185501.png', 'Сапожки детские «Снежинка» зимние на меху. Производитель: ООО «Тёплые ножки», г. Новосибирск', 'Верх — экокожа морозостойкая, утеплитель — искусственный мех (акрил 70%, полиэстер 30%), подкладка — флис, подошва — термоэластопласт (ТЭП)', 3490.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (5, 1, 'Сапоги', 'Сапожки детские «Медвежонок» демисезонные непромокаемые', 5, 'IMG_KB_164816.png', 'Сапожки детские «Медвежонок» демисезонные непромокаемые. Производитель: Компания «Северята», г. Архангельск', 'Верх — плащёвая ткань с водоотталкивающей пропиткой (полиэстер 100%), отделка — экокожа, подкладка — микрофибра, мембрана — AirTex, подошва — резина', 3190.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (6, 1, 'Сапоги', 'Сапожки детские «Принцесса» кожаные', 6, 'IMG_KB_164811.png', 'Сапожки детские «Принцесса» кожаные. Производитель: Мастерская «Весна», г. Тула', 'Верх — натуральная кожа (КРС), подкладка — шерсть натуральная (70%), байка (30%), стелька — войлочная, подошва — полиуретан', 4290.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (7, 1, 'Босоножки', 'Сандалии детские «Пчёлка» ортопедические летние', 7, 'IMG_KSd_195207.png', 'Сандалии детские «Пчёлка» ортопедические летние. Производитель: ООО «Здоровый шаг», г. Воронеж', 'Верх — нубук натуральный, подкладка — кожа растительного дубления, стелька — анатомическая с супинатором (латекс + пробка), подошва — каучук', 2790.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (8, 1, 'Босоножки', 'Сандалии детские «Морячок» текстильные с фиксатором', 8, 'IMG_KSd_185508.png', 'Сандалии детские «Морячок» текстильные с фиксатором. Производитель: ИП Кузнецов А.Д. (бренд «Карапуз»), г. Краснодар', 'Верх — джинсовая ткань (хлопок 100%), окантовка — искусственная кожа, подкладка — хлопок, подошва — ЭВА лёгкая', 1690.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (9, 1, 'Туфли', 'Туфли детские «Бантик» лаковые праздничные', 9, 'IMG_KSho_185512.png', 'Туфли детские «Бантик» лаковые праздничные. Производитель: Дом обуви «Маленький франт», г. Москва', 'Верх — искусственная лаковая кожа (ПВХ), носок усиленный — термопластичный полиуретан, подкладка — кожа искусственная дышащая, стелька — анатомическая с амортизацией, подошва — полиуретан', 2390.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (10, 10, 'Сапоги', 'Сапоги зимние натуральная кожа', 10, 'IMG_WB_170905.png', 'Сапоги женские зимние, нескользящая, устойчивая подошва, натуральный мех. Производитель: Дом обуви «Барбари», г. Новороссийск', 'Верх — натуральная кожа, подкладка — евромех, натуральный мех, текстильный утеплитель, подошва — резина', 25000.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (11, 10, 'Сапоги', 'Сапоги осенние натуральная кожа', 10, 'IMG_WB_170859.png', 'Сапоги женские демисезонные из высококачественной натуральной кожи. Производитель: Дом обуви «Барбари», г. Новороссийск', 'Верх — натуральная кожа, подкладка — текстильный утеплитель, стелька — текстиль, подошва — ТПР', 15000.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (12, 10, 'Сапоги', 'Сапоги трубы демисезонные замшевые', 12, 'IMG_WB_170906.png', 'Сапоги женские демисезонные замшевые. Производитель: ОАО «Твой комфорт», г. Ярославль', 'Верх — натуральная замша, утепленные, тракторная подошва, стелька — байка, подошва — резина', 17000.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (13, 10, 'Босоножки', 'Босоножки «Песчаный берег» коричневые', 13, 'IMG_WSd_174332.png', 'Коричневая кожаная модель с открытым носком, боковой пряжкой и закрытым каблуком. Производитель: ИП «Стиль и комфорт», г. Санкт-Петербург', 'Верх — 100% козья кожа, подкладка — 100% кожа; подошва: 100% кожа', 7500.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (14, 10, 'Босоножки', 'Женские босоножки «Черный кофе» со скульптурным каблуком', 14, 'IMG_WSd_185156.png', 'Открытый носок и ремешок со сборной пряжкой, низкий каблук и резиновая подошва гарантируют комфорт. Производитель: ЗАО «Кожевенные традиции», г. Вятка', 'Верх — кожа собственного производств, подкладка — кожа; подошва: резина', 5600.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (15, 10, 'Босоножки', 'Босоножки женские «Летний бриз»', 15, 'IMG_WSd_185551.png', 'Босоножки женские кожаные белые, регулируемый ремешок, закрытый каблук и кожаная подошва. Производитель: ООО «Модный силуэт», г. Кострома', 'Верх — натуральная кожа, подкладка — натуральная кожа, подошва — кожа', 7130.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (16, 10, 'Туфли', 'Демисезонные туфли натуральная кожа', 15, 'IMG_WSho_174409.png', 'Комфортные лаконичные лодочки, классический дизайна с современными акцентами. Производитель: ООО «Модный силуэт», г. Кострома', 'Верх — натуральная овечья кожа, подкладка и стелька — натуральная овечья кожа, подошва — резина', 12340.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (17, 10, 'Туфли', 'Туфли женские натуральная кожа с металлическими вставками', 14, 'IMG_WSho_185202.png', 'Стильные туфли для весеннего и летнего сезона. Производитель: ЗАО «Кожевенные традиции», г. Вятка', 'Верх — натуральная телячьей кожа, металлическая пряжка, подкладка и стелька— натуральная овечья кожа, подошва — резина', 7757.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (18, 10, 'Туфли', 'Туфли классические лодочки натуральная кожа', 13, 'IMG_WSho_185545.png', 'Модель из натуральной кожи, классический острый носок и изящная шпилька. Производитель: ИП «Стиль и комфорт», г. Санкт-Петербург', 'Верх — натуральная кожа, подкладка и стелька — натуральная кожа, подошва — тунит', 7550.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (19, 10, 'Кроссовки', 'Кроссовки белые с оранжевым и красным', 2, 'IMG_WS_174110.png', 'Многослойный верх из кожи и текстиля. Производитель: Фабрика «Топ-Топ», г. Киров', 'Верх — 70% кожа, 30% текстиль, подкладка — текстиль, подошва — резина', 9450.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (20, 10, 'Кроссовки', 'Кроссовки летние кожаные', 2, 'IMG_WS_185528.png', 'Уверенность на каждом шагу. Материал обеспечивает долговечность и комфорт при носке. Производитель: Фабрика «Топ-Топ», г. Киров', 'Верх — 87% кожа, 11% текстиль, 2% синтетика; подкладка: 100% текстиль; подошва: резина, пластик', 8565.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (21, 10, 'Кроссовки', 'Кроссовки кожаные', 13, 'IMG_WS_185535.png', 'Кроссовки женские из натуральной кожи. Производитель: ИП «Стиль и комфорт», г. Санкт-Петербург', 'Верх — натуральная кожа, подкладка — кожа, подошва — полиуретан', 8765.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (22, 10, 'Кроссовки', 'Кроссовки «Стиль и комфорт»', 13, 'IMG_WS_185538.png', 'Кроссовки женские из натуральной кожи и синтетических материалов, сетчатые вставки. Производитель: ИП «Стиль и комфорт», г. Санкт-Петербург', 'Верх — 70% кожа, 20% полиамид, 10% полиуретан; подкладка — текстиль, подошва — ТПУ', 7795.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (23, 23, 'Кроссовки', 'Кроссовки для бега «Драйв»', 23, 'IMG_MS_185531.png', 'Сочетание стиля, комфорта и современных технологий. Производитель: Фабрика «Азимут», г. Санкт-Петербург', 'Верх — сетка, подкладка — текстиль, подошва — резина', 6550.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (24, 23, 'Кроссовки', 'Кроссовки «Азимут Бег»', 23, 'IMG_MS_185532.png', 'Универсальный выбор для повседневного использования. Производитель: Фабрика «Азимут», г. Санкт-Петербург', 'Верх — 6% кожа, 29% текстиль, 15% полимерные материалы; подкладка — 100% текстиль; подошва — полимерные материалы, резина', 7890.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (25, 23, 'Кроссовки', 'Кроссовки', 2, 'IMG_MS_185533.png', 'Кроссовки для мужчин, идеальное сочетание стиля и комфорта. Производитель: Фабрика «Топ-Топ», г. Киров', 'Верх — 56% кожа, 29% текстиль, 15% полимерные материалы; подкладка — 100% текстиль; подошва — полимерные материалы, резина', 9567.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (26, 23, 'Туфли', 'Черные туфли в классическом стиле — база для деловых образов', 10, 'IMG_MSho_190514.png', 'Модель выполнена из натуральной кожи, на резиновой подошве. Производитель: Дом обуви «Барбари», г. Новороссийск', 'Верх — натуральная кожа, подкладка — текстиль, стелька — натуральная кожа, подошва — резина', 24569.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (27, 23, 'Туфли', 'Туфли мужские светлые классика демисезонные', 27, 'IMG_MSho_190518.png', 'Туфли на низком каблуке кожаные', 'Верх — натуральная кожа, подкладка — текстиль, стелька — натуральная кожа, подошва — ТЭП', 10155.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (28, 23, 'Туфли', 'Туфли из натуральной кожи', 27, 'IMG_MSho_191612.png', 'Модель выполнена из натуральной кожи, на резиновой подошве, поддеживает классический и деловой стиль образов. Производитель: Дом обуви «Берестов», г. Москва', 'Верх — натуральная кожа, подкладка — натуральная кожа, стелька — натуральная кожа, подошва — резина', 25625.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (29, 23, 'Ботинки', 'Ботинки мужские демисезонные', 10, 'IMG_MB_174349.png', 'Ботинки из натуральной кожи темно-коричневого и черного цвета на шнурках. Производитель: Дом обуви «Берестов», г. Москва', 'Верх — натуральная кожа, подкладка — текстиль, подошва — искусственный материал', 21500.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (30, 23, 'Ботинки', 'Ботинки черные из натуральной кожи', 14, 'IMG_MB_191200.png', 'Ботинки представляют баланс традиций и современности. Выполнены из натуральной кожи насыщенного черного цвета. Производитель: ЗАО «Кожевенные традиции», г. Вятка', 'Верх — натуральная кожа, подкладка — ворсин, стелька — ворсин, подошва — тунит', 14567.00);
INSERT INTO public.products (product_id, category_id, subcategory, product_name, manufacturer_id, image_path, description, composition, price) VALUES (31, 23, 'Ботинки', 'Ботинки зимние классические', 10, 'IMG_MB_191205.png', 'Выбор на каждый день — натуральная кожа, натуральный мех. Производитель: Дом обуви «Барбари», г. Новороссийск', 'Верх — натуральная кожа, подкладка — натуральный мех, стелька — натуральный мех, подошва — ТЭП', 15670.00);


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.roles (role_id, role_name) VALUES (1, 'Администратор');
INSERT INTO public.roles (role_id, role_name) VALUES (2, 'Менеджер');
INSERT INTO public.roles (role_id, role_name) VALUES (3, 'Авторизованный пользователь');


--
-- Data for Name: sizes; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sizes (size_id, size_value) VALUES (1, 18.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (2, 19.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (3, 20.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (4, 21.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (5, 22.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (6, 23.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (7, 24.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (8, 25.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (9, 26.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (10, 27.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (11, 28.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (12, 29.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (13, 30.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (14, 31.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (15, 32.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (16, 33.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (17, 34.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (18, 35.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (19, 36.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (20, 36.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (21, 37.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (22, 37.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (23, 38.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (24, 38.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (25, 39.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (26, 39.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (27, 40.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (28, 40.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (29, 41.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (30, 41.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (31, 42.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (32, 42.5);
INSERT INTO public.sizes (size_id, size_value) VALUES (33, 43.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (34, 44.0);
INSERT INTO public.sizes (size_id, size_value) VALUES (35, 45.0);


--
-- Data for Name: stock_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (1, 1, 3, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (2, 1, 4, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (3, 1, 5, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (4, 1, 6, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (5, 1, 7, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (6, 1, 8, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (7, 2, 16, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (8, 2, 17, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (9, 3, 2, 30);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (10, 3, 3, 30);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (11, 4, 2, 15);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (12, 4, 3, 15);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (13, 5, 4, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (14, 5, 5, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (15, 5, 6, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (16, 6, 1, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (17, 6, 2, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (18, 6, 3, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (19, 7, 4, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (20, 7, 5, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (21, 7, 6, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (22, 7, 7, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (23, 8, 10, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (24, 8, 11, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (25, 8, 12, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (26, 8, 13, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (27, 9, 1, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (28, 9, 2, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (29, 9, 3, 7);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (30, 10, 19, 12);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (31, 10, 21, 12);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (32, 11, 25, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (33, 11, 27, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (34, 12, 21, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (35, 12, 25, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (36, 12, 27, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (37, 13, 19, 10);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (38, 13, 21, 10);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (39, 13, 23, 10);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (40, 13, 25, 10);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (41, 13, 27, 10);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (42, 14, 18, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (43, 15, 21, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (44, 15, 25, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (45, 15, 27, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (46, 16, 19, 25);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (47, 16, 21, 25);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (48, 16, 23, 25);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (49, 17, 19, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (50, 17, 23, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (51, 17, 25, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (52, 17, 27, 4);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (53, 18, 18, 9);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (54, 18, 23, 9);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (55, 19, 18, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (56, 19, 19, 2);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (57, 20, 21, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (58, 20, 22, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (59, 20, 23, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (60, 20, 24, 5);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (61, 21, 18, 16);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (62, 21, 19, 16);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (63, 21, 23, 16);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (64, 21, 25, 16);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (65, 22, 18, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (66, 22, 23, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (67, 23, 30, 18);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (68, 23, 31, 18);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (69, 23, 32, 18);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (70, 23, 33, 18);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (71, 24, 23, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (72, 24, 24, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (73, 24, 25, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (74, 24, 26, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (75, 24, 27, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (76, 24, 29, 50);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (77, 25, 29, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (78, 25, 31, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (79, 25, 34, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (80, 26, 27, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (81, 26, 29, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (82, 26, 33, 23);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (83, 27, 31, 15);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (84, 27, 33, 15);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (85, 27, 34, 15);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (86, 28, 34, 3);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (87, 29, 29, 1);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (88, 29, 31, 1);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (89, 30, 31, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (90, 30, 33, 20);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (91, 31, 29, 30);
INSERT INTO public.stock_items (stock_item_id, product_id, size_id, quantity_available) VALUES (92, 31, 31, 30);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (1, 'Иванов', 'Иван', 'Сергеевич', 'isivanov', 1);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (2, 'Петров', 'Пётр', 'Алексеевич', 'papetrov', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (3, 'Сидорова', 'Анна', 'Дмитриевна', 'asidorova', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (4, 'Кузнецова', 'Екатерина', 'Андреевна', 'ekuznetsova', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (5, 'Смирнов', 'Дмитрий', 'Владимирович', 'dsmirnov', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (6, 'Попов', 'Алексей', 'Николаевич', 'apopov', 1);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (7, 'Васильева', 'Ольга', 'Игоревна', 'ovasileva', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (8, 'Соколов', 'Павел', 'Викторович', 'psokolov', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (9, 'Михайлова', 'Татьяна', 'Юрьевна', 'tmikhailova', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (10, 'Новикова', 'Наталья', 'Сергеевна', 'nnovikova', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (11, 'Фёдоров', 'Андрей', 'Максимович', 'afedorov', 1);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (12, 'Морозов', 'Сергей', 'Павлович', 'smorozov', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (13, 'Волкова', 'Юлия', 'Александровна', 'jvolkova', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (14, 'Алексеев', 'Артём', 'Евгеньевич', 'aalekseev', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (15, 'Лебедева', 'Ирина', 'Владимировна', 'ilebedeva', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (16, 'Егоров', 'Никита', 'Денисович', 'negorov', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (17, 'Павлова', 'Елена', 'Петровна', 'epavlova', 3);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (18, 'Козлов', 'Роман', 'Олегович', 'rkozlov', 1);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (19, 'Степанова', 'Виктория', 'Романовна', 'vstepanova', 2);
INSERT INTO public.users (user_id, last_name, first_name, middle_name, login, role_id) VALUES (20, 'Николаев', 'Владимир', 'Иванович', 'vnikolaev', 3);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 31, true);


--
-- Name: manufacturers_manufacturer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.manufacturers_manufacturer_id_seq', 31, true);


--
-- Name: order_items_order_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_order_item_id_seq', 30, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 11, false);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_product_id_seq', 31, true);


--
-- Name: roles_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_role_id_seq', 20, true);


--
-- Name: sizes_size_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sizes_size_id_seq', 127, true);


--
-- Name: stock_items_stock_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_items_stock_item_id_seq', 92, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 20, true);


--
-- Name: categories categories_category_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_category_name_key UNIQUE (category_name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: manufacturers manufacturers_manufacturer_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manufacturers
    ADD CONSTRAINT manufacturers_manufacturer_name_key UNIQUE (manufacturer_name);


--
-- Name: manufacturers manufacturers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (manufacturer_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_item_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: products products_product_name_manufacturer_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_product_name_manufacturer_id_key UNIQUE (product_name, manufacturer_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- Name: sizes sizes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sizes
    ADD CONSTRAINT sizes_pkey PRIMARY KEY (size_id);


--
-- Name: sizes sizes_size_value_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sizes
    ADD CONSTRAINT sizes_size_value_key UNIQUE (size_value);


--
-- Name: stock_items stock_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_items
    ADD CONSTRAINT stock_items_pkey PRIMARY KEY (stock_item_id);


--
-- Name: stock_items stock_items_product_id_size_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_items
    ADD CONSTRAINT stock_items_product_id_size_id_key UNIQUE (product_id, size_id);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_orders_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_orders_user_id ON public.orders USING btree (user_id);


--
-- Name: ix_stock_items_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stock_items_product_id ON public.stock_items USING btree (product_id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_stock_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_stock_item_id_fkey FOREIGN KEY (stock_item_id) REFERENCES public.stock_items(stock_item_id) ON DELETE RESTRICT;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE RESTRICT;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE RESTRICT;


--
-- Name: products products_manufacturer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES public.manufacturers(manufacturer_id) ON DELETE RESTRICT;


--
-- Name: stock_items stock_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_items
    ADD CONSTRAINT stock_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: stock_items stock_items_size_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_items
    ADD CONSTRAINT stock_items_size_id_fkey FOREIGN KEY (size_id) REFERENCES public.sizes(size_id) ON DELETE RESTRICT;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--


