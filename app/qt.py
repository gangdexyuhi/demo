"""Единая точка импорта Qt: PyQt6, а если его нет (старый Python) — PyQt5."""
try:
    from PyQt6 import QtCore, QtGui, QtWidgets  # noqa: F401
    QT_API = "PyQt6"
except ImportError:  # pragma: no cover - запасной вариант для Python 3.8 на ROSA Linux
    from PyQt5 import QtCore, QtGui, QtWidgets  # noqa: F401
    QT_API = "PyQt5"

Qt = QtCore.Qt
