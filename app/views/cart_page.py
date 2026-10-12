"""Оформление заказа: состав формируемого заказа, изменение, подтверждение."""
from app.data import orders_repo
from app.data.users_repo import can_manage_orders, full_name, get_users
from app.db import DatabaseError
from app.discount import format_rub, pairs_text
from app.messages import ask_confirmation, show_error, show_info, show_warning
from app.qt import QtWidgets, Qt
from app.views.base_page import BasePage, make_button

COLUMNS = ["Модель", "Производство", "Размер", "Количество", "Цена за ед.", "Сумма", ""]


class CartPage(BasePage):
    page_title = "Оформление заказа"

    def __init__(self, main_window):
        super().__init__(main_window)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        client_layout = QtWidgets.QHBoxLayout()
        self.client_caption = QtWidgets.QLabel("Клиент:")
        client_layout.addWidget(self.client_caption)
        self.client_combo = QtWidgets.QComboBox()
        self.client_combo.setMinimumWidth(320)
        client_layout.addWidget(self.client_combo)
        client_layout.addStretch(1)
        layout.addLayout(client_layout)

        self.table = QtWidgets.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(COLUMNS)):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.empty_label = QtWidgets.QLabel("Заказ пуст. Вернитесь в каталог и выберите модель обуви.")
        self.empty_label.setObjectName("hint")
        layout.addWidget(self.empty_label)

        bottom_layout = QtWidgets.QHBoxLayout()
        self.total_label = QtWidgets.QLabel()
        self.total_label.setObjectName("totalLabel")
        bottom_layout.addWidget(self.total_label, 1)

        continue_button = make_button("Продолжить выбор", secondary=True)
        continue_button.clicked.connect(lambda: self.main_window.go_back_to("catalog"))
        bottom_layout.addWidget(continue_button)
        self.cancel_button = make_button("Отказаться от заказа", secondary=True)
        self.cancel_button.clicked.connect(self.cancel_order)
        bottom_layout.addWidget(self.cancel_button)
        self.confirm_button = make_button("Подтвердить заказ")
        self.confirm_button.clicked.connect(self.confirm_order)
        bottom_layout.addWidget(self.confirm_button)
        layout.addLayout(bottom_layout)

    def on_show(self, **kwargs):
        manager_mode = can_manage_orders(self.current_user)
        self.client_caption.setVisible(manager_mode)
        self.client_combo.setVisible(manager_mode)
        if manager_mode:
            self.load_clients()
        self.fill_table()

    def load_clients(self):
        """Менеджер/администратор выбирает, на какого клиента оформить заказ."""
        selected_id = self.draft.client_id or self.current_user["user_id"]
        self.client_combo.clear()
        try:
            for user in get_users():
                self.client_combo.addItem("{} ({})".format(full_name(user), user["login"]), user["user_id"])
        except DatabaseError as error:
            show_error(self, str(error))
            return
        self.client_combo.setCurrentIndex(max(self.client_combo.findData(selected_id), 0))

    def fill_table(self):
        items = self.draft.items
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._set_text(row, 0, item["product_name"])
            self._set_text(row, 1, item["manufacturer_name"])
            self._set_text(row, 2, item["size_text"])

            quantity_spin = QtWidgets.QSpinBox()
            quantity_spin.setRange(1, max(item["available"], 1))
            quantity_spin.setValue(item["quantity"])
            quantity_spin.setToolTip("Доступно для заказа: {}".format(pairs_text(item["available"])))
            # Значение по умолчанию в лямбде фиксирует текущую позицию,
            # иначе все спинбоксы ссылались бы на последнюю строку цикла.
            quantity_spin.valueChanged.connect(lambda value, current=item: self.change_quantity(current, value))
            self.table.setCellWidget(row, 3, quantity_spin)

            self._set_text(row, 4, format_rub(item["price"]))
            self._set_text(row, 5, format_rub(item["price"] * item["quantity"]))

            remove_button = make_button("Удалить", secondary=True)
            remove_button.clicked.connect(lambda _checked=False, current=item: self.remove_item(current))
            self.table.setCellWidget(row, 6, remove_button)
        self.table.resizeRowsToContents()
        self.update_totals()

    def _set_text(self, row, column, text):
        cell = QtWidgets.QTableWidgetItem(str(text))
        if column >= 2:
            cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, column, cell)

    def update_totals(self):
        is_empty = self.draft.is_empty()
        self.empty_label.setVisible(is_empty)
        self.confirm_button.setEnabled(not is_empty)
        self.cancel_button.setEnabled(not is_empty)
        self.total_label.setText(
            "Итого: {} на сумму {}".format(pairs_text(self.draft.total_pairs()), format_rub(self.draft.total_sum()))
        )
        for row, item in enumerate(self.draft.items):
            self._set_text(row, 5, format_rub(item["price"] * item["quantity"]))

    def change_quantity(self, item, value):
        item["quantity"] = value
        self.update_totals()

    def remove_item(self, item):
        question = "Удалить из заказа «{}», размер {}?".format(item["product_name"], item["size_text"])
        if not ask_confirmation(self, question):
            return
        self.draft.remove(item["stock_item_id"])
        self.fill_table()

    def cancel_order(self):
        if not ask_confirmation(self, "Отказаться от оформления заказа?\nВсе выбранные позиции будут удалены."):
            return
        self.draft.clear()
        show_info(self, "Оформление заказа отменено.")
        self.main_window.go_back_to("catalog")

    def confirm_order(self):
        if self.draft.is_empty():
            show_warning(self, "Заказ пуст. Добавьте товары из каталога.")
            return
        client_id = self.current_user["user_id"]
        if can_manage_orders(self.current_user) and self.client_combo.currentData() is not None:
            client_id = self.client_combo.currentData()
        if not ask_confirmation(
            self,
            "Подтвердить заказ: {} на сумму {}?".format(
                pairs_text(self.draft.total_pairs()), format_rub(self.draft.total_sum())
            ),
        ):
            return
        try:
            order_id = orders_repo.create_order(client_id, self.draft.items)
        except orders_repo.OrderError as error:
            show_warning(self, str(error))
            return
        except DatabaseError as error:
            show_error(self, str(error))
            return
        self.draft.clear()
        show_info(
            self,
            "Заказ №{} успешно оформлен.\nДоступное количество товаров в каталоге обновлено.".format(order_id),
        )
        # Менеджер возвращается к списку заказов, клиент — в каталог
        if "orders" in self.main_window.history:
            self.main_window.go_back_to("orders")
        else:
            self.main_window.go_back_to("catalog")
