"""Главное окно: шапка (логотип, заголовок, ФИО пользователя) и стек страниц.

Навигация последовательная: каждая страница открывается поверх предыдущей,
кнопка «Назад» возвращает на прошлую страницу.
"""
from config import APP_NAME
from app.data.users_repo import full_name, is_authorized
from app.discount import pairs_text
from app.messages import ask_confirmation
from app.order_draft import OrderDraft
from app.paths import ICON_PATH, LOGO_PATH
from app.qt import QtGui, QtWidgets, Qt
from app.views.base_page import make_button
from app.views.cart_page import CartPage
from app.views.catalog_page import CatalogPage
from app.views.login_page import LoginPage
from app.views.order_details_page import OrderDetailsPage
from app.views.orders_page import OrdersPage
from app.views.product_page import ProductPage


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.order_draft = OrderDraft()
        self.history = []

        self.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))
        self.resize(1100, 760)
        self.setMinimumSize(900, 600)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_header())

        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.pages = {
            "login": LoginPage(self),
            "catalog": CatalogPage(self),
            "product": ProductPage(self),
            "cart": CartPage(self),
            "orders": OrdersPage(self),
            "order_details": OrderDetailsPage(self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        self.reset_to("login")

    def _build_header(self):
        header = QtWidgets.QFrame()
        header.setObjectName("headerBar")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        logo_label = QtWidgets.QLabel()
        # Логотип масштабируем с сохранением пропорций (требование руководства по стилю)
        logo_pixmap = QtGui.QPixmap(str(LOGO_PATH)).scaled(
            64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)

        self.back_button = make_button("← Назад", secondary=True)
        self.back_button.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_button)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("pageTitle")
        header_layout.addWidget(self.title_label, 1)

        self.user_label = QtWidgets.QLabel()
        self.user_label.setObjectName("userName")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.user_label)

        self.logout_button = make_button("Выйти", secondary=True)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        return header

    # ---------- навигация ----------

    def navigate(self, page_name, **kwargs):
        self.history.append(page_name)
        self._show(page_name, **kwargs)

    def go_back(self):
        if len(self.history) <= 1:
            return
        self.history.pop()
        self._show(self.history[-1])

    def reset_to(self, page_name, **kwargs):
        self.history = [page_name]
        self._show(page_name, **kwargs)

    def go_back_to(self, page_name):
        """Возврат к ранее открытой странице с удалением промежуточных из истории."""
        while len(self.history) > 1 and self.history[-1] != page_name:
            self.history.pop()
        if self.history[-1] != page_name:
            self.history = [page_name]
        self._show(page_name)

    def _show(self, page_name, **kwargs):
        page = self.pages[page_name]
        page.on_show(**kwargs)
        self.stack.setCurrentWidget(page)
        self.update_header()

    def update_header(self):
        page = self.stack.currentWidget()
        self.title_label.setText(page.page_title)
        self.setWindowTitle("{} — {}".format(APP_NAME, page.page_title))
        self.back_button.setVisible(len(self.history) > 1)
        logged_in = self.current_user is not None
        self.user_label.setText(full_name(self.current_user) if logged_in else "")
        self.logout_button.setVisible(logged_in)

    # ---------- вход / выход ----------

    def login(self, user):
        self.current_user = user
        self.order_draft.clear()
        self.reset_to("catalog")

    def logout(self):
        if is_authorized(self.current_user) and not self.order_draft.is_empty():
            if not ask_confirmation(
                self,
                "У вас есть неподтверждённый заказ ({}).\n"
                "При выходе он будет удалён. Выйти?".format(pairs_text(self.order_draft.total_pairs())),
            ):
                return
        self.current_user = None
        self.order_draft.clear()
        self.reset_to("login")
