"""Окна сообщений обратной связи: ошибка, предупреждение, информация, подтверждение.

У каждого типа свой заголовок и пиктограмма, как требует ТЗ.
"""
from app.qt import QtWidgets

QMessageBox = QtWidgets.QMessageBox


def show_error(parent, text):
    QMessageBox.critical(parent, "Ошибка", text)


def show_warning(parent, text):
    QMessageBox.warning(parent, "Предупреждение", text)


def show_info(parent, text):
    QMessageBox.information(parent, "Информация", text)


def ask_confirmation(parent, text):
    """Вопрос перед необратимой операцией. По умолчанию выбрано «Нет»."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle("Подтверждение")
    box.setText(text)
    yes_button = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
    no_button = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
    box.setDefaultButton(no_button)
    box.exec()
    return box.clickedButton() is yes_button
