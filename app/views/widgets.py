"""Общие виджеты: изображение товара и карточка товара по макету."""
from app.discount import format_rub, pairs_text
from app.paths import IMAGES_DIR, PLACEHOLDER_PATH
from app.qt import QtCore, QtGui, QtWidgets, Qt

LOW_STOCK_LIMIT = 3


def load_product_pixmap(image_path, width, height):
    """Картинка товара; если файла нет или он повреждён — заглушка picture.png."""
    pixmap = QtGui.QPixmap()
    if image_path:
        pixmap = QtGui.QPixmap(str(IMAGES_DIR / image_path))
    if pixmap.isNull():
        pixmap = QtGui.QPixmap(str(PLACEHOLDER_PATH))
    return pixmap.scaled(
        width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )


def make_price_label(product, object_name="cardPrice"):
    """Цена со скидкой; при наличии скидки старая цена выводится зачёркнутой."""
    label = QtWidgets.QLabel()
    label.setObjectName(object_name)
    if product["has_discount"]:
        label.setText(
            "<span style='font-size:15px; color:#555555; text-decoration:line-through;'>{}</span><br>{}".format(
                format_rub(product["price"]), format_rub(product["final_price"])
            )
        )
        label.setToolTip("Скидка 25 %: на модель не было заказов в прошлом месяце")
    else:
        label.setText(format_rub(product["final_price"]))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


class ProductCard(QtWidgets.QFrame):
    """Карточка модели: изображение | производство, наименование, категория, количество, состав | цена."""

    clicked = QtCore.pyqtSignal(int)

    def __init__(self, product, clickable=True):
        super().__init__()
        self.product_id = product["product_id"]
        self.clickable = clickable
        self.setObjectName("productCard")
        is_low_stock = product["total_quantity"] <= LOW_STOCK_LIMIT
        # Свойство lowStock включает светло-красный фон из styles.qss
        self.setProperty("lowStock", is_low_stock)
        if clickable:
            self.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
            self.setToolTip("Нажмите, чтобы открыть карточку товара")

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 24, 12)
        layout.setSpacing(24)

        image_label = QtWidgets.QLabel()
        image_label.setFixedSize(180, 130)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(load_product_pixmap(product["image_path"], 180, 130))
        layout.addWidget(image_label)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(4)
        title = QtWidgets.QLabel("{} | {}".format(product["manufacturer_name"], product["product_name"]))
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        info_layout.addWidget(title)
        info_layout.addWidget(QtWidgets.QLabel("Категория: {}".format(product["category_name"])))
        quantity_text = "Количество: {}".format(pairs_text(product["total_quantity"]))
        if is_low_stock:
            quantity_text += " — осталось мало"
        info_layout.addWidget(QtWidgets.QLabel(quantity_text))
        composition = QtWidgets.QLabel("Состав: {}".format(product["composition"] or "не указан"))
        composition.setObjectName("cardSmall")
        composition.setWordWrap(True)
        info_layout.addWidget(composition)
        info_layout.addStretch(1)
        layout.addLayout(info_layout, 1)

        price_label = make_price_label(product)
        price_label.setMinimumWidth(170)
        layout.addWidget(price_label)

    def mouseReleaseEvent(self, event):  # noqa: N802 — имя метода задано Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.product_id)
        super().mouseReleaseEvent(event)
