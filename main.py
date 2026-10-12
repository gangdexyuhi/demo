"""«Чудо Обувь» — система оформления заказа обуви. Точка входа.

Запуск из корня проекта:  python main.py
"""
import sys
import traceback

from app.messages import show_error
from app.paths import ICON_PATH, STYLE_PATH
from app.qt import QtGui, QtWidgets
from app.views.main_window import MainWindow
from config import APP_NAME


def handle_unexpected_error(error_type, error, error_traceback):
    """Любая непредвиденная ошибка показывается окном, а приложение не закрывается."""
    traceback.print_exception(error_type, error, error_traceback)
    show_error(
        QtWidgets.QApplication.activeWindow(),
        "Произошла непредвиденная ошибка:\n{}\n\n"
        "Повторите действие. Если ошибка повторяется, сообщите администратору.".format(error),
    )


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))
    app.setFont(QtGui.QFont("Calibri", 11))
    try:
        app.setStyleSheet(STYLE_PATH.read_text(encoding="utf-8"))
    except OSError:
        print("Файл стилей не найден: {}".format(STYLE_PATH))
    sys.excepthook = handle_unexpected_error

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
