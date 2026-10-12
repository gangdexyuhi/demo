"""Пути к ресурсам приложения (работают и из исходников, и из собранного .exe)."""
import sys
from pathlib import Path

# PyInstaller распаковывает ресурсы во временную папку sys._MEIPASS
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

RESOURCES_DIR = BASE_DIR / "resources"
IMAGES_DIR = RESOURCES_DIR / "images"
LOGO_PATH = RESOURCES_DIR / "logo.png"
ICON_PATH = RESOURCES_DIR / "icon.ico"
PLACEHOLDER_PATH = RESOURCES_DIR / "picture.png"
STYLE_PATH = RESOURCES_DIR / "styles.qss"
