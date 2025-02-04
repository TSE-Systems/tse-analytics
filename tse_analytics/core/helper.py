import sqlite3
from base64 import b64encode
from io import BytesIO
from pathlib import Path

from matplotlib.figure import Figure

from tse_analytics.core import messaging

IS_RELEASE = Path("_internal").exists()

CSV_IMPORT_ENABLED = True


def show_help(sender, filename: str) -> None:
    docs_path = Path("_internal/docs/topics") if IS_RELEASE else Path("../docs/topics")
    path = docs_path / Path(filename)
    if path.exists():
        with open(path, encoding="utf-8") as file:
            content = file.read().rstrip()
            if content is not None:
                content = (
                    content.replace("](", "](_internal/docs/images/")
                    if IS_RELEASE
                    else content.replace("](", "](../docs/images/")
                )
                messaging.broadcast(messaging.ShowHelpMessage(sender, content))


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
