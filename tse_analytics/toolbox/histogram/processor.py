from dataclasses import dataclass

import pandas as pd
import seaborn.objects as so
from matplotlib import pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class HistogramResult:
    report: str


def get_histogram_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable_name: str,
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> HistogramResult:
    match split_mode:
        case SplitMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            by = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            by = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
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
