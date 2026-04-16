from dataclasses import dataclass

import pandas as pd
import seaborn.objects as so
from matplotlib import pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import Variable
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
    grouping_settings: GroupingSettings,
    error_bar: str,
    figsize: tuple[float, float] | None = None,
) -> DataPlotResult:
    columns = datatable.get_default_columns() + list(datatable.dataset.factors) + list(variables)
    df = datatable.get_filtered_df(columns)
    df["Hours"] = df["Timedelta"] / pd.Timedelta(1, "h")

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.RUN:
            by = "Run"
            palette = color_manager.get_run_to_color_dict(datatable.dataset.runs)
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[by])
        case _:
            by = None
            palette = color_manager.colormap_name

    # TODO: workaround for issue with nullable Float64
    df[variables.keys()] = df[variables.keys()].astype(float)

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    plot = (
        so
        .Plot(
            df,
            x="Hours",
            color=by,
        )
        .pair(y=list(variables))
        .add(so.Line(linewidth=1.0), so.Agg(func="mean"))
    )

    if error_bar is not None:
        plot = plot.add(so.Band(alpha=0.15), so.Est(errorbar=error_bar))

    (
        plot
        .scale(
            color=so.Nominal(palette, order=df[by].cat.categories.tolist())
            if (grouping_settings.mode == GroupingMode.ANIMAL or grouping_settings.mode == GroupingMode.FACTOR)
            else palette,
        )
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
