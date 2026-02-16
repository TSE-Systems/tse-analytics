from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from ptitprince import RainCloud

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class DistributionResult:
    report: str


def get_distribution_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable_name: str,
    split_mode: SplitMode,
    factor_name: str | None,
    plot_type: str,
    show_points: bool,
    figsize: tuple[float, float] | None = None,
) -> DistributionResult:
    match split_mode:
        case SplitMode.ANIMAL:
            x = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            x = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            x = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
        case _:
            x = None
            palette = color_manager.colormap_name

    if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
        df[x] = df[x].cat.remove_unused_categories()

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")

    ax = figure.add_subplot(1, 1, 1)
    ax.tick_params(axis="x", rotation=90)

    match plot_type:
        case "Raincloud plot":
            RainCloud(
                data=df,
                x=x,
                y=variable_name,
                hue=x,
                ax=ax,
                width_viol=0.5,
            )
        case "Violin plot":
            sns.violinplot(
                data=df,
                x=x,
                y=variable_name,
                hue=x,
                palette=palette,
                inner="quartile" if show_points else "box",
                saturation=1,
                fill=not show_points,
                legend=False,
                ax=ax,
            )
        case "Box plot":
            sns.boxplot(
                data=df,
                x=x,
                y=variable_name,
                hue=x,
                palette=palette,
                saturation=1,
                fill=not show_points,
                legend=False,
                gap=0.1,
                ax=ax,
            )

    if show_points and plot_type != "Raincloud plot":
        sns.stripplot(
            data=df,
            x=x,
            y=variable_name,
            hue=x,
            palette=palette,
            legend=False,
            marker=".",
            ax=ax,
        )

    report = get_html_image_from_figure(figure)

    return DistributionResult(
        report=report,
    )
