"""Список заказов (Менеджер и Администратор)."""
from app.data import orders_repo
from app.data.users_repo import can_edit_orders, can_manage_orders, full_name
from app.db import DatabaseError
from app.discount import format_rub, pairs_text
from app.messages import ask_confirmation, show_error, show_info, show_warning
from app.qt import QtWidgets, Qt
from app.views.base_page import BasePage, make_button

COLUMNS = ["№ заказа", "Дата заказа", "ФИО клиента", "Пар", "Сумма"]


class OrdersPage(BasePage):
    page_title = "Список заказов"

    def __init__(self, main_window):
        super().__init__(main_window)
        self.orders = []
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        hint = QtWidgets.QLabel("Дважды щёлкните по заказу, чтобы открыть его состав.")
        hint.setObjectName("hint")
        layout.addWidget(hint)

        self.table = QtWidgets.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for column in (0, 1, 3, 4):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.doubleClicked.connect(lambda _index: self.open_order())
        layout.addWidget(self.table, 1)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.total_label = QtWidgets.QLabel()
        self.total_label.setObjectName("hint")
        buttons_layout.addWidget(self.total_label, 1)

        self.delete_button = make_button("Удалить заказ", secondary=True)
        self.delete_button.clicked.connect(self.delete_order)
        buttons_layout.addWidget(self.delete_button)
        self.edit_button = make_button("Редактировать")
        self.edit_button.clicked.connect(lambda: self.open_order(edit_mode=True))
        buttons_layout.addWidget(self.edit_button)
        open_button = make_button("Состав заказа")
        open_button.clicked.connect(lambda: self.open_order())
        buttons_layout.addWidget(open_button)
        add_button = make_button("Новый заказ")
        add_button.clicked.connect(self.add_order)
        buttons_layout.addWidget(add_button)
        layout.addLayout(buttons_layout)

    def on_show(self, **kwargs):
        self.edit_button.setVisible(can_edit_orders(self.current_user))
        self.load_orders()

    def load_orders(self):
        try:
            self.orders = orders_repo.get_orders()
        except DatabaseError as error:
            show_error(self, str(error))
            self.orders = []
        self.table.setRowCount(len(self.orders))
        for row, order in enumerate(self.orders):
            values = [
                str(order["order_id"]),
                order["order_date"].strftime("%d.%m.%Y"),
                full_name(order),
                str(order["total_pairs"]),
                format_rub(order["total_sum"]),
            ]
            for column, value in enumerate(values):
                cell = QtWidgets.QTableWidgetItem(value)
                if column != 2:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, cell)
        self.total_label.setText("Всего заказов: {}".format(len(self.orders)))

    def _selected_order(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.orders) or not self.table.selectedItems():
            show_warning(self, "Сначала выберите заказ в списке (щёлкните по строке).")
            return None
        return self.orders[row]

    def open_order(self, edit_mode=False):
        order = self._selected_order()
        if order is None:
            return
        # Повторная проверка роли: кнопку скрыли, но редактирование
        # должно быть недоступно не-администратору при любом способе вызова.
        if edit_mode and not can_edit_orders(self.current_user):
            show_warning(self, "Редактировать заказы может только администратор.")
            return
        self.main_window.navigate("order_details", order_id=order["order_id"], edit_mode=edit_mode)

    def add_order(self):
        if not can_manage_orders(self.current_user):
            show_warning(self, "Добавлять заказы могут только менеджер и администратор.")
            return
        if not self.draft.is_empty() and not ask_confirmation(
            self, "Есть неподтверждённый заказ ({}). Продолжить его оформление?\n"
                  "«Нет» — начать новый заказ с пустым составом.".format(pairs_text(self.draft.total_pairs()))
        ):
            self.draft.clear()
        show_info(
            self,
            "Выберите модели в каталоге (используйте поиск по наименованию), "
            "укажите размер и количество, затем откройте «Текущий заказ», "
            "выберите клиента и подтвердите заказ.",
        )
        self.main_window.navigate("catalog")

    def delete_order(self):
        order = self._selected_order()
        if order is None:
            return
        if not ask_confirmation(
            self,
            "Удалить заказ №{} от {} ({})?\nСостав заказа будет удалён, пары вернутся на склад. "
            "Это действие нельзя отменить.".format(
                order["order_id"], order["order_date"].strftime("%d.%m.%Y"), full_name(order)
            ),
        ):
            return
        try:
            orders_repo.delete_order(order["order_id"])
        except orders_repo.OrderError as error:
            show_warning(self, str(error))
        except DatabaseError as error:
            show_error(self, "Не удалось удалить заказ №{}.\n{}".format(order["order_id"], error))
        else:
            show_info(self, "Заказ №{} удалён.".format(order["order_id"]))
        self.load_orders()
