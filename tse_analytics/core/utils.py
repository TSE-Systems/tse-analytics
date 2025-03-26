import sqlite3
from base64 import b64encode
from datetime import time
from io import BytesIO
from pathlib import Path

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QToolButton, QWidget, QWidgetAction, QSizePolicy
from matplotlib.figure import Figure

IS_RELEASE = Path("_internal").exists()

CSV_IMPORT_ENABLED = True


def get_html_image(figure: Figure) -> str:
    io = BytesIO()
    figure.savefig(io, format="png")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br/>"


def get_available_sqlite_tables(path: Path) -> list[str]:
    with sqlite3.connect(path, check_same_thread=False) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        cursor.close()
    return [item[0] for item in tables]


def get_widget_tool_button(parent: QWidget, widget: QWidget, text: str, icon: QIcon) -> QToolButton:
    button = QToolButton(
        parent,
        popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
    )
    button.setText(text)
    button.setIcon(icon)

    widget_action = QWidgetAction(parent)
    widget_action.setDefaultWidget(widget)
    button.addAction(widget_action)
    return button


def get_h_spacer_widget(parent: QWidget) -> QWidget:
    widget = QWidget(parent)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    return widget


def time_to_float(value: time) -> float:
    return value.hour + value.minute / 60.0
