from dataclasses import dataclass

import matplotlib.pyplot as plt
import seaborn.objects as so

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class HistogramResult:
    report: str


def get_histogram_result(
    datatable: Datatable,
    variable_name: str,
    factor_name: str,
    figsize: tuple[float, float] | None = None,
) -> HistogramResult:
    columns = [factor_name, variable_name]
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    (
        so
        .Plot(
            df,
            x=variable_name,
            color=factor_name,
        )
        .facet(col=factor_name, wrap=3)
        .add(so.Bars(), so.Hist())
        .scale(color=palette)
        .on(figure)
        .plot(True)
    )

    report = get_html_image_from_figure(figure)

    return HistogramResult(
        report=report,
    )
