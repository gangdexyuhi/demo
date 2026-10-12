"""Форма просмотра модели обуви и добавления выбранного размера в заказ."""
from app.data import catalog_repo
from app.data.catalog_repo import format_size
from app.db import DatabaseError
from app.discount import pairs_text
from app.messages import show_error, show_info, show_warning
from app.qt import QtWidgets, Qt
from app.views.base_page import BasePage, make_button
from app.views.widgets import load_product_pixmap, make_price_label


class ProductPage(BasePage):
    page_title = "Карточка товара"

    def __init__(self, main_window):
        super().__init__(main_window)
        self.product_id = None
        self.product = None
        self.stock_items = []

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(32)

        left_layout = QtWidgets.QVBoxLayout()
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(360, 280)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)
        self.price_container = QtWidgets.QVBoxLayout()
        left_layout.addLayout(self.price_container)
        left_layout.addStretch(1)
        layout.addLayout(left_layout)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(8)
        self.form = QtWidgets.QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.manufacturer_label = self._add_field("Производство:")
        self.name_label = self._add_field("Наименование:")
        self.category_label = self._add_field("Категория:")
        self.composition_label = self._add_field("Состав:")
        self.description_label = self._add_field("Описание:")
        self.size_range_label = self._add_field("Размерный ряд:")
        right_layout.addLayout(self.form)

        order_box = QtWidgets.QFrame()
        order_box.setObjectName("toolBar")
        order_layout = QtWidgets.QGridLayout(order_box)
        order_layout.setContentsMargins(12, 12, 12, 12)
        order_title = QtWidgets.QLabel("Добавить в заказ")
        order_title.setObjectName("sectionTitle")
        order_layout.addWidget(order_title, 0, 0, 1, 2)

        order_layout.addWidget(QtWidgets.QLabel("Доступный размер:"), 1, 0)
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.currentIndexChanged.connect(self.update_quantity_limit)
        order_layout.addWidget(self.size_combo, 1, 1)

        order_layout.addWidget(QtWidgets.QLabel("Количество пар:"), 2, 0)
        # QSpinBox принимает только целые числа в заданном диапазоне —
        # ввести отрицательное, дробное или нечисловое значение невозможно.
        self.quantity_spin = QtWidgets.QSpinBox()
        self.quantity_spin.setMinimum(1)
        order_layout.addWidget(self.quantity_spin, 2, 1)

        self.limit_hint = QtWidgets.QLabel()
        self.limit_hint.setObjectName("hint")
        order_layout.addWidget(self.limit_hint, 3, 0, 1, 2)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.add_button = make_button("Добавить в заказ")
        self.add_button.clicked.connect(self.add_to_order)
        buttons_layout.addWidget(self.add_button)
        self.cart_button = make_button("Перейти к заказу", secondary=True)
        self.cart_button.clicked.connect(lambda: self.main_window.navigate("cart"))
        buttons_layout.addWidget(self.cart_button)
        order_layout.addLayout(buttons_layout, 4, 0, 1, 2)
        right_layout.addWidget(order_box)
        right_layout.addStretch(1)
        layout.addLayout(right_layout, 1)

    def _add_field(self, caption):
        value_label = QtWidgets.QLabel()
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.form.addRow(QtWidgets.QLabel("<b>{}</b>".format(caption)), value_label)
        return value_label

    def on_show(self, product_id=None, **kwargs):
        # При возврате «Назад» product_id не передаётся — показываем прежнюю модель
        if product_id is not None:
            self.product_id = product_id
        self.load_product()

    def load_product(self):
        try:
            self.product = catalog_repo.get_product(self.product_id)
            self.stock_items = catalog_repo.get_stock_items(self.product_id)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        if self.product is None:
            show_warning(self, "Модель не найдена в базе данных. Возможно, она была удалена.")
            return

        product = self.product
        self.image_label.setPixmap(load_product_pixmap(product["image_path"], 360, 280))
        self.manufacturer_label.setText(product["manufacturer_name"])
        self.name_label.setText(product["product_name"])
        category_text = product["category_name"]
        if product["subcategory"]:
            category_text += " / " + product["subcategory"]
        self.category_label.setText(category_text)
        self.composition_label.setText(product["composition"] or "не указан")
        self.description_label.setText(product["description"] or "нет описания")
        size_range = [format_size(item["size_value"]) for item in self.stock_items]
        self.size_range_label.setText(", ".join(size_range) if size_range else "нет размеров")

        # Пересоздаём блок цены: она могла измениться (скидка зависит от даты)
        while self.price_container.count():
            old_widget = self.price_container.takeAt(0).widget()
            if old_widget is not None:
                old_widget.deleteLater()
        self.price_container.addWidget(make_price_label(product))

        self.size_combo.blockSignals(True)
        self.size_combo.clear()
        for item in self.stock_items:
            # Остаток с учётом того, что уже лежит в формируемом заказе
            free_quantity = item["quantity_available"] - self.draft.quantity_in_draft(item["stock_item_id"])
            if free_quantity > 0:
                size_caption = "{} (доступно {})".format(format_size(item["size_value"]), pairs_text(free_quantity))
                self.size_combo.addItem(size_caption, item["stock_item_id"])
        self.size_combo.blockSignals(False)
        self.update_quantity_limit()

    def _selected_stock_item(self):
        stock_item_id = self.size_combo.currentData()
        for item in self.stock_items:
            if item["stock_item_id"] == stock_item_id:
                return item
        return None

    def update_quantity_limit(self):
        stock_item = self._selected_stock_item()
        has_sizes = stock_item is not None
        self.size_combo.setEnabled(has_sizes)
        self.quantity_spin.setEnabled(has_sizes)
        self.add_button.setEnabled(has_sizes)
        if not has_sizes:
            self.limit_hint.setText("Нет доступных для заказа размеров этой модели.")
            return
        free_quantity = stock_item["quantity_available"] - self.draft.quantity_in_draft(stock_item["stock_item_id"])
        self.quantity_spin.setMaximum(max(free_quantity, 1))
        self.quantity_spin.setValue(1)
        self.limit_hint.setText("Можно заказать от 1 до {}.".format(pairs_text(free_quantity)))

    def add_to_order(self):
        stock_item = self._selected_stock_item()
        if stock_item is None:
            show_warning(self, "Выберите размер из списка доступных.")
            return
        quantity = self.quantity_spin.value()
        free_quantity = stock_item["quantity_available"] - self.draft.quantity_in_draft(stock_item["stock_item_id"])
        if quantity <= 0 or quantity > free_quantity:
            show_warning(
                self,
                "Количество должно быть от 1 до {} для выбранного размера.\n"
                "Измените количество и повторите.".format(pairs_text(free_quantity)),
            )
            return
        size_text = format_size(stock_item["size_value"])
        self.draft.add(self.product, stock_item, size_text, quantity)
        show_info(
            self,
            "В заказ добавлено: «{}», размер {}, {}.\n"
            "Продолжите выбор в каталоге или нажмите «Перейти к заказу», "
            "чтобы подтвердить заказ.".format(self.product["product_name"], size_text, pairs_text(quantity)),
        )
        self.load_product()
