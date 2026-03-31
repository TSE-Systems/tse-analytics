from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class HistogramResult:
    report: str


def get_histogram_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable_name: str,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> HistogramResult:
    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case GroupingMode.RUN:
            by = "Run"
            palette = color_manager.colormap_name
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[by])
        case _:
            by = None
            palette = color_manager.colormap_name

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
