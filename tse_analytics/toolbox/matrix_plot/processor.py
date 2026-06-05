from dataclasses import dataclass
from typing import Literal

import seaborn as sns
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
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


def get_matrix_plot_result(
    datatable: Datatable,
    variables: list[str],
    factor_name: str,
    plot_kind: Literal["scatter", "kde", "hist", "reg"],
    figsize: tuple[float, float] | None = None,
) -> MatrixPlotResult:
    columns = [factor_name] + variables
    df = datatable.get_filtered_df(columns)

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    pair_grid = sns.pairplot(
        df[[factor_name] + variables] if factor_name is not None else df[variables],
        hue=factor_name,
        kind=plot_kind,
        diag_kind="auto",
        palette=palette,
        markers=".",
    )
    if figsize is None:
        figsize = rcParams["figure.figsize"]
    pair_grid.figure.set_size_inches(figsize)
    pair_grid.figure.set_layout_engine("tight")
    # sns.move_legend(pair_grid, "upper right")
    # pair_grid.map_lower(sns.kdeplot, levels=4, color=".2")

    report = get_html_image_from_figure(pair_grid.figure)

    return MatrixPlotResult(
        report=report,
    )
