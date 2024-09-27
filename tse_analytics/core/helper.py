from base64 import b64encode
from io import BytesIO
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import ShowHelpMessage
from tse_analytics.core.pretty_html_table import build_table

LAYOUT_VERSION = 9
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


def build_df_table(df: pd.DataFrame, color="grey_light", font_size="11pt", padding="5px", font_family="Arial") -> str:
    return build_table(
        df=df,
        color=color,
        font_size=font_size,
        padding=padding,
        font_family=font_family,
    )
