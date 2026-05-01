from dataclasses import dataclass

import matplotlib.pyplot as plt
import seaborn as sns
from ptitprince import RainCloud

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class DistributionResult:
    report: str


def get_distribution_result(
    datatable: Datatable,
    variable_name: str,
    grouping_settings: GroupingSettings,
    plot_type: str,
    show_points: bool,
    figsize: tuple[float, float] | None = None,
) -> DistributionResult:
    columns = get_columns_by_grouping_settings(grouping_settings, [variable_name])
    df = datatable.get_filtered_df(columns)

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            x = "Animal"
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.FACTOR:
            x = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[x])

    if grouping_settings.mode == GroupingMode.ANIMAL or grouping_settings.mode == GroupingMode.FACTOR:
        # TODO: temporary fix for issue with broken categories offset when using pandas 3.0
        df.sort_values(x, inplace=True)
        df[x] = df[x].astype("string")

    # Create a figure with a tight layout
    figure, ax = plt.subplots(1, 1, figsize=figsize, layout="tight")
    ax.tick_params(axis="x", rotation=90)

    match plot_type:
        case "Raincloud plot":
            RainCloud(
                data=df,
                x=x,
                y=variable_name,
                hue=x,
                palette=palette,
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
