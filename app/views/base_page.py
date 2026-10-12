"""Базовый класс страницы приложения."""
from app.qt import QtWidgets


class BasePage(QtWidgets.QWidget):
    # Заголовок страницы: выводится в шапке и в заголовке окна
    page_title = ""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    @property
    def current_user(self):
        return self.main_window.current_user

    @property
    def draft(self):
        return self.main_window.order_draft

    def on_show(self, **kwargs):
        """Вызывается при каждом переходе на страницу — здесь перечитываем данные."""


def make_button(text, secondary=False):
    button = QtWidgets.QPushButton(text)
    if secondary:
        # Свойство используется в styles.qss для второстепенных кнопок
        button.setProperty("secondary", True)
    return button
