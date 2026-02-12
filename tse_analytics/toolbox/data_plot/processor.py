from dataclasses import dataclass

import pandas as pd
import seaborn.objects as so
from matplotlib import pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_html_image_from_figure, time_to_float

ERROR_BAR_TYPE: dict[str, str | None] = {
    "None": None,
    "Confidence Interval": "ci",
    "Percentile Interval": "pi",
    "Standard Error": "se",
    "Standard Deviation": "sd",
}


@dataclass
class DataPlotResult:
    report: str


def get_data_plot_result(
    datatable: Datatable,
    variables: dict[str, Variable],
    split_mode: SplitMode,
    factor_name: str | None,
    error_bar: str,
    figsize: tuple[float, float] | None = None,
) -> DataPlotResult:
    columns = datatable.get_default_columns() + list(datatable.dataset.factors) + list(variables)
    df = datatable.get_filtered_df(columns)

    df["Hours"] = df["Timedelta"] / pd.Timedelta(1, "h")

    match split_mode:
        case SplitMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case SplitMode.RUN:
            by = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            by = factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
        case _:
            by = None
            palette = color_manager.colormap_name

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    (
        so
        .Plot(
            df,
            x="Hours",
            color=by,
        )
        .pair(y=list(variables))
        .add(so.Line(linewidth=1.0), so.Agg(func="mean"))  # Line with mean estimate
        .add(so.Band(alpha=0.15), so.Est(errorbar=error_bar))  # Shaded CI band
        .scale(color=palette)
        .on(figure)
        .plot(True)
    )

    settings = datatable.dataset.binning_settings.time_cycles_settings

    dark_start = time_to_float(settings.dark_cycle_start)
    dark_end = time_to_float(settings.light_cycle_start)
    dark_duration = abs(dark_end - dark_start)
    max_hours = df["Hours"].max()

    experiment_started_time = time_to_float(datatable.dataset.experiment_started.time())
    time_shift = abs(experiment_started_time - dark_start)
    start = time_shift
    while start < max_hours:
        for ax in figure.axes:
            ax.axvspan(start, start + dark_duration, color="gray", alpha=0.15)
        start = 24 + start

    report = get_html_image_from_figure(figure)

    return DataPlotResult(
        report=report,
    )
