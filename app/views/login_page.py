"""Страница входа: только логин, пароль не требуется."""
import re

from app.data.users_repo import find_user_by_login, make_guest
from app.db import DatabaseError
from app.messages import show_error, show_warning
from app.paths import LOGO_PATH
from app.qt import QtCore, QtGui, QtWidgets, Qt
from app.views.base_page import BasePage, make_button

# Логин из списка пользователей: латиница, цифры, точка, _ и -
LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


class LoginPage(BasePage):
    page_title = "Вход в систему"

    def __init__(self, main_window):
        super().__init__(main_window)
        outer = QtWidgets.QVBoxLayout(self)
        outer.addStretch(1)

        form = QtWidgets.QVBoxLayout()
        form.setSpacing(12)

        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap(str(LOGO_PATH)).scaled(
            180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addWidget(logo)

        caption = QtWidgets.QLabel("Введите логин из списка пользователей системы")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addWidget(caption)

        self.login_input = QtWidgets.QLineEdit()
        self.login_input.setPlaceholderText("Логин, например: isivanov")
        self.login_input.setMaxLength(50)
        # Валидатор не даёт ввести символы, которых не бывает в логине
        self.login_input.setValidator(QtGui.QRegularExpressionValidator(
            QtCore.QRegularExpression(r"[A-Za-z0-9._-]{0,50}"), self.login_input
        ))
        self.login_input.returnPressed.connect(self.try_login)
        form.addWidget(self.login_input)

        login_button = make_button("Войти")
        login_button.clicked.connect(self.try_login)
        form.addWidget(login_button)

        guest_button = make_button("Продолжить как гость", secondary=True)
        guest_button.clicked.connect(self.login_as_guest)
        form.addWidget(guest_button)

        hint = QtWidgets.QLabel("Гость может только просматривать каталог товаров.")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addWidget(hint)

        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        container = QtWidgets.QWidget()
        container.setLayout(form)
        container.setFixedWidth(380)
        row.addWidget(container)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(2)

    def on_show(self, **kwargs):
        self.login_input.clear()
        self.login_input.setFocus()

    def try_login(self):
        login = self.login_input.text().strip()
        if not login:
            show_warning(self, "Поле «Логин» не заполнено.\nВведите логин и нажмите «Войти».")
            return
        if not LOGIN_PATTERN.match(login):
            show_warning(self, "Логин может содержать только латинские буквы, цифры и символы . _ -")
            return
        try:
            user = find_user_by_login(login)
        except DatabaseError as error:
            show_error(self, str(error))
            return
        if user is None:
            show_error(
                self,
                "Пользователь с логином «{}» не найден.\n"
                "Проверьте раскладку клавиатуры и правильность логина "
                "или войдите как гость.".format(login),
            )
            return
        self.main_window.login(user)

    def login_as_guest(self):
        self.main_window.login(make_guest())

