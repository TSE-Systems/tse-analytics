from dataclasses import dataclass

import matplotlib.pyplot as plt
import pingouin as pg

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure, get_plot_layout


@dataclass
class NormalityTestResult:
    report: str


def get_normality_result(
    datatable: Datatable,
    variable_name: str,
    factor_name: str,
    figsize: tuple[float, float] | None = None,
) -> NormalityTestResult:
    columns = [factor_name, variable_name]
    df = datatable.get_filtered_df(columns)

    if factor_name == "Animal":
        figure = plt.Figure(figsize=(figsize[0], figsize[0] * df["Animal"].nunique() / 9), layout="tight")
    else:
        figure = plt.Figure(figsize=figsize, layout="tight")

    levels = df[factor_name].unique()
    nrows, ncols = get_plot_layout(len(levels))
    for index, level in enumerate(levels):
        ax = figure.add_subplot(nrows, ncols, index + 1)
        pg.qqplot(
            df[df[factor_name] == level][variable_name],
            dist="norm",
            marker=".",
            ax=ax,
        )
        ax.set_title(level)

    report = get_html_image_from_figure(figure)

    return NormalityTestResult(
        report=report,
    )
