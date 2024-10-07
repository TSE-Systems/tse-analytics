import sqlite3
from base64 import b64encode
from io import BytesIO
from pathlib import Path

from loguru import logger
import pandas as pd
from PySide6.QtWidgets import QWidget
from matplotlib.figure import Figure
from pyqttoast import Toast, ToastPreset, ToastPosition

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import ShowHelpMessage
from tse_analytics.core.pretty_html_table import build_table

LAYOUT_VERSION = 10
IS_RELEASE = Path("_internal").exists()

CSV_IMPORT_ENABLED = True


def show_help(sender, filename: str) -> None:
    docs_path = Path("_internal/docs") if IS_RELEASE else Path("../docs")
    path = docs_path / Path(filename)
    if path.exists():
        with open(path, encoding="utf-8") as file:
            content = file.read().rstrip()
            if content is not None:
                content = (
                    content.replace("](", "](_internal/docs/") if IS_RELEASE else content.replace("](", "](../docs/")
                )
                Manager.messenger.broadcast(ShowHelpMessage(sender, content))


def get_html_image(figure: Figure) -> str:
    io = BytesIO()
    figure.savefig(io, format="png")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br/>"


def get_available_sqlite_tables(path: Path) -> set[str]:
    with sqlite3.connect(path, check_same_thread=False) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        cursor.close()
    return set([item[0] for item in tables])


def build_df_table(df: pd.DataFrame, color="grey_light", font_size="11pt", padding="5px", font_family="Arial") -> str:
    return build_table(
        df=df,
        color=color,
        font_size=font_size,
        padding=padding,
        font_family=font_family,
    )


def make_toast(
    parent: QWidget,
    title: str,
    text: str,
    duration=0,
    preset=ToastPreset.INFORMATION,
    position=ToastPosition.CENTER,
    show_duration_bar=False,
    echo_to_logger=False,
) -> Toast:
    toast = Toast(parent)
    toast.setTitle(title)
    toast.setText(text)
    toast.setDuration(duration)
    toast.applyPreset(preset)
    toast.setPosition(position)
    toast.setShowCloseButton(False)
    toast.setShowDurationBar(show_duration_bar)
    if echo_to_logger:
        match preset:
            case ToastPreset.INFORMATION:
                logger.info(text)
            case ToastPreset.WARNING:
                logger.warning(text)
            case ToastPreset.ERROR:
                logger.error(text)
            case ToastPreset.SUCCESS:
                logger.success(text)
            case _:
                logger.info(text)
    return toast
