"""HTML image and table generation utilities."""

from base64 import b64encode
from io import BytesIO

import pandas as pd
import seaborn.objects as so
from matplotlib.figure import Figure


def get_html_image_from_figure(figure: Figure) -> str:
    """Convert a matplotlib figure to an HTML image tag with embedded base64 data.

    This function saves the figure as a PNG image in memory, encodes it as base64,
    and returns an HTML img tag that can be used to display the image in HTML content.

    Args:
        figure: The matplotlib Figure object to convert.

    Returns:
        A string containing an HTML img tag with the figure embedded as base64 data.
    """
    io = BytesIO()
    figure.savefig(io, format="png", bbox_inches="tight")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br>"


def get_html_image_from_plot(plot: so.Plot) -> str:
    io = BytesIO()
    plot.save(io, format="png", bbox_inches="tight")
    encoded = b64encode(io.getvalue()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}'><br>"


def get_html_table(df: pd.DataFrame, caption: str, precision=5, index=True) -> str:
    styler = df.style.set_caption(caption).format(precision=precision)
    if not index:
        styler = styler.hide(axis="index")
    return styler.to_html()


def get_plot_layout(number_of_elements: int) -> tuple[int, int]:
    if number_of_elements == 1:
        return 1, 1
    elif number_of_elements == 2:
        return 1, 2
    elif number_of_elements <= 4:
        return 2, 2
    else:
        return round(number_of_elements / 3) + 1, 3
