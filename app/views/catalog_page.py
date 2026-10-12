"""Главная страница: каталог моделей обуви с поиском, фильтром и сортировкой."""
from app.data import catalog_repo
from app.data.users_repo import can_manage_orders, is_authorized
from app.db import DatabaseError
from app.discount import pairs_text
from app.messages import show_error, show_info
from app.qt import QtWidgets
from app.views.base_page import BasePage, make_button
from app.views.widgets import ProductCard

ALL_CATEGORIES_TEXT = "Все категории"


class CatalogPage(BasePage):
    page_title = "Каталог товаров"

    def __init__(self, main_window):
        super().__init__(main_window)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        # ----- панель поиска/фильтра/сортировки (только для авторизованных) -----
        self.tool_bar = QtWidgets.QFrame()
        self.tool_bar.setObjectName("toolBar")
        tool_layout = QtWidgets.QHBoxLayout(self.tool_bar)
        tool_layout.setContentsMargins(12, 8, 12, 8)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Поиск по наименованию и описанию")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMaxLength(100)
        tool_layout.addWidget(self.search_input, 2)

        self.category_combo = QtWidgets.QComboBox()
        tool_layout.addWidget(self.category_combo, 1)

        self.sort_combo = QtWidgets.QComboBox()
        self.sort_combo.addItem("Без сортировки", catalog_repo.SORT_NONE)
        self.sort_combo.addItem("Цена по возрастанию", catalog_repo.SORT_PRICE_ASC)
        self.sort_combo.addItem("Цена по убыванию", catalog_repo.SORT_PRICE_DESC)
        tool_layout.addWidget(self.sort_combo, 1)
        layout.addWidget(self.tool_bar)

        # Поиск, фильтр и сортировка применяются сразу при изменении
        self.search_input.textChanged.connect(self.refresh_products)
        self.category_combo.currentIndexChanged.connect(self.refresh_products)
        self.sort_combo.currentIndexChanged.connect(self.refresh_products)

        # ----- строка состояния и кнопки действий -----
        actions_layout = QtWidgets.QHBoxLayout()
        self.count_label = QtWidgets.QLabel()
        self.count_label.setObjectName("hint")
        actions_layout.addWidget(self.count_label, 1)

        self.orders_button = make_button("Заказы")
        self.orders_button.clicked.connect(lambda: self.main_window.navigate("orders"))
        actions_layout.addWidget(self.orders_button)

        self.cart_button = make_button("Текущий заказ")
        self.cart_button.clicked.connect(lambda: self.main_window.navigate("cart"))
        actions_layout.addWidget(self.cart_button)
        layout.addLayout(actions_layout)

        # ----- список карточек -----
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.addStretch(1)
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area, 1)

    def on_show(self, **kwargs):
        authorized = is_authorized(self.current_user)
        self.tool_bar.setVisible(authorized)
        self.cart_button.setVisible(authorized)
        self.orders_button.setVisible(can_manage_orders(self.current_user))
        if not authorized:
            # Гостю фильтры недоступны — сбрасываем их, чтобы показать весь каталог
            self.search_input.blockSignals(True)
            self.search_input.clear()
            self.search_input.blockSignals(False)
            self.sort_combo.blockSignals(True)
            self.sort_combo.setCurrentIndex(0)
            self.sort_combo.blockSignals(False)
        self.load_categories()
        self.update_cart_button()
        self.refresh_products()

    def load_categories(self):
        """Заполняет фильтр категориями из БД, сохраняя выбранную категорию."""
        selected_id = self.category_combo.currentData()
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(ALL_CATEGORIES_TEXT, None)
        try:
            for category in catalog_repo.get_categories():
                self.category_combo.addItem(category["category_name"], category["category_id"])
        except DatabaseError as error:
            show_error(self, str(error))
        selected_index = self.category_combo.findData(selected_id)
        if not is_authorized(self.current_user):
            selected_index = 0
        self.category_combo.setCurrentIndex(max(selected_index, 0))
        self.category_combo.blockSignals(False)

    def update_cart_button(self):
        pairs = self.draft.total_pairs()
        self.cart_button.setText("Текущий заказ ({})".format(pairs_text(pairs)) if pairs else "Текущий заказ")

    def refresh_products(self):
        try:
            products = catalog_repo.get_products(
                search_text=self.search_input.text(),
                category_id=self.category_combo.currentData(),
                sort_mode=self.sort_combo.currentData(),
            )
            total_count = len(catalog_repo.get_products())
        except DatabaseError as error:
            show_error(self, str(error))
            return

        # Удаляем старые карточки (последний элемент — растяжка, её оставляем)
        while self.cards_layout.count() > 1:
            widget = self.cards_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        for product in products:
            card = ProductCard(product, clickable=True)
            card.clicked.connect(self.open_product)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        if products:
            self.count_label.setText("Показано {} из {} моделей".format(len(products), total_count))
        else:
            self.count_label.setText("Ничего не найдено — измените строку поиска или выберите другую категорию")

    def open_product(self, product_id):
        if not is_authorized(self.current_user):
            show_info(
                self,
                "Оформлять заказы могут только авторизованные пользователи.\n"
                "Нажмите «Выйти» и войдите в систему по своему логину.",
            )
            return
        self.main_window.navigate("product", product_id=product_id)
