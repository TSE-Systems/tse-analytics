from dataclasses import dataclass

import matplotlib.pyplot as plt
import seaborn.objects as so

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class HistogramResult:
    report: str


def get_histogram_result(
    datatable: Datatable,
    variable_name: str,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> HistogramResult:
    columns = get_columns_by_grouping_settings(grouping_settings, [variable_name])
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            # Cleaning
            df[by] = df[by].cat.remove_unused_categories()
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.RUN:
            by = "Run"
            palette = color_manager.get_run_to_color_dict(datatable.dataset.runs)
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[by])

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    (
        so
        .Plot(
            df,
            x=variable_name,
            color=by,
        )
        .facet(col=by, wrap=3)
        .add(so.Bars(), so.Hist())
        .scale(color=palette)
        .on(figure)
        .plot(True)
    )

    report = get_html_image_from_figure(figure)

    return HistogramResult(
        report=report,
    )
