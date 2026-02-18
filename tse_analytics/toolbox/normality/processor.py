from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import pingouin as pg

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure, get_plot_layout


@dataclass
class NormalityTestResult:
    report: str


def get_normality_result(
    df: pd.DataFrame,
    variable_name: str,
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> NormalityTestResult:
    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")

    match split_mode:
        case SplitMode.ANIMAL:
            by = "Animal"
        case SplitMode.RUN:
            by = "Run"
        case SplitMode.FACTOR:
            by = factor_name
        case _:
            by = None

    if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
        df[by] = df[by].cat.remove_unused_categories()

    match split_mode:
        case SplitMode.ANIMAL:
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
        case SplitMode.FACTOR:
            levels = df[factor_name].unique()
            nrows, ncols = get_plot_layout(len(levels))
            for index, level in enumerate(levels):
                # TODO: NaN check
                if level != level:
                    continue
                ax = figure.add_subplot(nrows, ncols, index + 1)
                pg.qqplot(
                    df[df[factor_name] == level][variable_name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title(level)
        case SplitMode.RUN:
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
        case SplitMode.TOTAL:
            ax = figure.add_subplot(1, 1, 1)
            pg.qqplot(
                df[variable_name],
                dist="norm",
                marker=".",
                ax=ax,
            )
            ax.set_title("Total")

    report = get_html_image_from_figure(figure)

    return NormalityTestResult(
        report=report,
    )
