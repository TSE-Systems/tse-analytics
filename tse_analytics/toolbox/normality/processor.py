from dataclasses import dataclass

import matplotlib.pyplot as plt
import pingouin as pg

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure, get_plot_layout
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class NormalityTestResult:
    report: str


def get_normality_result(
    datatable: Datatable,
    variable_name: str,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> NormalityTestResult:
    columns = get_columns_by_grouping_settings(grouping_settings, [variable_name])
    df = datatable.get_filtered_df(columns)

    if grouping_settings.mode == GroupingMode.ANIMAL:
        figure = plt.Figure(figsize=(figsize[0], figsize[0] * df["Animal"].nunique() / 9), layout="tight")
    else:
        figure = plt.Figure(figsize=figsize, layout="tight")

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            animals = df["Animal"].unique()
            nrows, ncols = get_plot_layout(len(animals))
            for index, animal in enumerate(animals):
                ax = figure.add_subplot(nrows, ncols, index + 1)
                pg.qqplot(
                    df[df["Animal"] == animal][variable_name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title(f"Animal: {animal}")
        case GroupingMode.FACTOR:
            levels = df[grouping_settings.factor_name].unique()
            nrows, ncols = get_plot_layout(len(levels))
            for index, level in enumerate(levels):
                ax = figure.add_subplot(nrows, ncols, index + 1)
                pg.qqplot(
                    df[df[grouping_settings.factor_name] == level][variable_name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title(level)
        case GroupingMode.RUN:
            runs = df["Run"].unique()
            nrows, ncols = get_plot_layout(len(runs))
            for index, run in enumerate(runs):
                ax = figure.add_subplot(nrows, ncols, index + 1)
                pg.qqplot(
                    df[df["Run"] == run][variable_name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title(f"Run: {run}")

    report = get_html_image_from_figure(figure)

    return NormalityTestResult(
        report=report,
    )
