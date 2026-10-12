"""Состав заказа; для администратора — редактирование даты и удаление позиций."""
from datetime import date

from app.data import orders_repo
from app.data.catalog_repo import format_size
from app.data.users_repo import can_edit_orders, full_name
from app.db import DatabaseError
from app.discount import format_rub, pairs_text
from app.messages import ask_confirmation, show_error, show_info, show_warning
from app.qt import QtCore, QtWidgets, Qt
from app.views.base_page import BasePage, make_button

COLUMNS = ["Модель", "Производство", "Размер", "Количество", "Цена за ед.", "Сумма"]


class OrderDetailsPage(BasePage):
    page_title = "Состав заказа"

    def __init__(self, main_window):
        super().__init__(main_window)
        self.order_id = None
        self.edit_mode = False
        self.items = []
        self.removed_item_ids = set()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        info_layout = QtWidgets.QHBoxLayout()
        self.order_label = QtWidgets.QLabel()
        self.order_label.setObjectName("sectionTitle")
        info_layout.addWidget(self.order_label)
        info_layout.addStretch(1)
        info_layout.addWidget(QtWidgets.QLabel("Дата заказа:"))
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        # Дата заказа не может быть в будущем
        self.date_edit.setMaximumDate(QtCore.QDate.currentDate())
        self.date_edit.setMinimumDate(QtCore.QDate(2000, 1, 1))
        info_layout.addWidget(self.date_edit)
        layout.addLayout(info_layout)

        self.table = QtWidgets.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for column in range(1, len(COLUMNS)):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, 1)

        bottom_layout = QtWidgets.QHBoxLayout()
        self.total_label = QtWidgets.QLabel()
        self.total_label.setObjectName("totalLabel")
        bottom_layout.addWidget(self.total_label, 1)
        self.remove_item_button = make_button("Удалить позицию", secondary=True)
        self.remove_item_button.clicked.connect(self.remove_selected_item)
        bottom_layout.addWidget(self.remove_item_button)
        self.cancel_button = make_button("Отменить изменения", secondary=True)
        self.cancel_button.clicked.connect(self.cancel_changes)
        bottom_layout.addWidget(self.cancel_button)
        self.save_button = make_button("Сохранить")
        self.save_button.clicked.connect(self.save_changes)
        bottom_layout.addWidget(self.save_button)
        layout.addLayout(bottom_layout)

    def on_show(self, order_id=None, edit_mode=False, **kwargs):
        if order_id is not None:
            self.order_id = order_id
            # Режим редактирования включается только администратору
            self.edit_mode = edit_mode and can_edit_orders(self.current_user)
        self.page_title = "Редактирование заказа" if self.edit_mode else "Состав заказа"
        for widget in (self.remove_item_button, self.cancel_button, self.save_button):
            widget.setVisible(self.edit_mode)
        self.date_edit.setReadOnly(not self.edit_mode)
        self.date_edit.setCalendarPopup(self.edit_mode)
        self.load_order()

    def load_order(self):
        self.removed_item_ids = set()
        try:
            order = orders_repo.get_order(self.order_id)
            self.items = orders_repo.get_order_items(self.order_id) if order else []
        except DatabaseError as error:
            show_error(self, str(error))
            return
        if order is None:
            show_warning(self, "Заказ №{} не найден — возможно, он был удалён.".format(self.order_id))
            self.main_window.go_back_to("orders")
            return
        self.order_label.setText("Заказ №{} — {}".format(order["order_id"], full_name(order)))
        order_date = order["order_date"]
        # Если старая дата позже сегодняшней (неверные данные) — расширяем допустимый диапазон
        self.date_edit.setMaximumDate(QtCore.QDate(max(order_date, date.today())))
        self.date_edit.setDate(QtCore.QDate(order_date.year, order_date.month, order_date.day))
        self.fill_table()

    def _visible_items(self):
        return [item for item in self.items if item["order_item_id"] not in self.removed_item_ids]

    def fill_table(self):
        items = self._visible_items()
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                item["product_name"],
                item["manufacturer_name"],
                format_size(item["size_value"]),
                str(item["quantity"]),
                format_rub(item["price"]),
                format_rub(item["line_sum"]),
            ]
            for column, value in enumerate(values):
                cell = QtWidgets.QTableWidgetItem(value)
                if column >= 2:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, cell)
        total_sum = sum(item["line_sum"] for item in items)
        total_pairs = sum(item["quantity"] for item in items)
        self.total_label.setText("Итоговая сумма: {} ({})".format(format_rub(total_sum), pairs_text(total_pairs)))

    def remove_selected_item(self):
        items = self._visible_items()
        row = self.table.currentRow()
        if row < 0 or row >= len(items) or not self.table.selectedItems():
            show_warning(self, "Выберите позицию заказа, которую нужно удалить.")
            return
        if len(items) == 1:
            show_warning(
                self,
                "В заказе должна остаться хотя бы одна позиция.\n"
                "Чтобы убрать все позиции, удалите заказ целиком в списке заказов.",
            )
            return
        item = items[row]
        if not ask_confirmation(
            self, "Удалить позицию «{}», размер {}?\nИзменение сохранится после нажатия «Сохранить».".format(
                item["product_name"], format_size(item["size_value"]))
        ):
            return
        self.removed_item_ids.add(item["order_item_id"])
        self.fill_table()

    def cancel_changes(self):
        if self.removed_item_ids and not ask_confirmation(self, "Отменить несохранённые изменения заказа?"):
            return
        self.main_window.go_back()

    def save_changes(self):
        if not can_edit_orders(self.current_user):
            show_warning(self, "Редактировать заказы может только администратор.")
            return
        new_date = self.date_edit.date().toPyDate()
        if new_date > date.today():
            show_warning(self, "Дата заказа не может быть позже сегодняшней. Исправьте дату.")
            return
        try:
            orders_repo.update_order(self.order_id, new_date, self.removed_item_ids)
        except orders_repo.OrderError as error:
            show_warning(self, str(error))
            return
        except DatabaseError as error:
            show_error(self, "Не удалось сохранить заказ.\n{}".format(error))
            return
        show_info(self, "Изменения заказа №{} сохранены.".format(self.order_id))
        self.main_window.go_back_to("orders")
