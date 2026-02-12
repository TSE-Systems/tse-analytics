from dataclasses import dataclass
from typing import Literal

import pandas as pd
import seaborn as sns
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure

MATRIXPLOT_KIND: dict[str, Literal["scatter", "kde", "hist", "reg"]] = {
    "Scatter Plot": "scatter",
    "Histogram": "hist",
    "Kernel Density Estimate": "kde",
    "Regression": "reg",
}


@dataclass
class MatrixPlotResult:
    report: str


def get_matrixplot_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    split_mode: SplitMode,
    factor_name: str | None,
    plot_kind: Literal["scatter", "kde", "hist", "reg"],
    figsize: tuple[float, float] | None = None,
) -> MatrixPlotResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    match split_mode:
        case SplitMode.ANIMAL:
            hue = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            hue = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            hue = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
        case _:  # Total
            hue = "None"
            palette = color_manager.colormap_name

    pair_grid = sns.pairplot(
        df[[hue] + variables] if hue is not None else df[variables],
        hue=hue,
        kind=plot_kind,
        diag_kind="auto",
        palette=palette,
        markers=".",
    )
    pair_grid.figure.set_size_inches(figsize)
    pair_grid.figure.set_layout_engine("tight")
    # sns.move_legend(pair_grid, "upper right")
    # pair_grid.map_lower(sns.kdeplot, levels=4, color=".2")

    report = get_html_image_from_figure(pair_grid.figure)

    return MatrixPlotResult(
        report=report,
    )
