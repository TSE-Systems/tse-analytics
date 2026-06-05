from dataclasses import dataclass

import pandas as pd
import seaborn.objects as so
from matplotlib import pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import ByTimeOfDayConfig, Variable
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


def compute_dark_band_spans(
    light_cycles: ByTimeOfDayConfig,
    experiment_started: pd.Timestamp,
    max_hours: float,
) -> list[tuple[float, float]]:
    """Compute the dark-cycle shading spans for a time-series plot.

    Hours are measured from the experiment start. The dark cycle wraps around
    midnight and may be asymmetric or reversed, so modular arithmetic is used
    (mirroring ``_apply_by_time_of_day``). Each span is clamped to the visible
    ``[0, max_hours]`` range.

    Args:
        light_cycles: The dataset's light/dark cycle configuration.
        experiment_started: The experiment start timestamp.
        max_hours: The right edge of the plotted range, in hours.

    Returns:
        A list of ``(start, end)`` hour spans that fall within the dark cycle.
    """
    dark_start = time_to_float(light_cycles.dark_cycle_start)
    dark_end = time_to_float(light_cycles.light_cycle_start)
    dark_duration = (dark_end - dark_start) % 24
    if dark_duration == 0:
        return []

    experiment_started_time = time_to_float(experiment_started.time())
    # Hours from experiment start to the first dark onset; step back one day so a
    # dark period already underway at t=0 is also shaded.
    time_shift = (dark_start - experiment_started_time) % 24
    spans: list[tuple[float, float]] = []
    start = time_shift - 24
    while start < max_hours:
        band_start = max(start, 0.0)
        band_end = min(start + dark_duration, max_hours)
        if band_end > band_start:
            spans.append((band_start, band_end))
        start += 24
    return spans


def get_data_plot_result(
    datatable: Datatable,
    variables: dict[str, Variable],
    factor_name: str,
    error_bar: str,
    figsize: tuple[float, float] | None = None,
) -> DataPlotResult:
    columns = datatable.get_default_columns() + list(datatable.dataset.factors) + list(variables)
    df = datatable.get_filtered_df(columns)
    df["Hours"] = df["Timedelta"] / pd.Timedelta(1, "h")

    # TODO: workaround for issue with nullable Float64
    df[variables.keys()] = df[variables.keys()].astype(float)

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    plot = (
        so
        .Plot(
            df,
            x="Hours",
            color=factor_name,
        )
        .pair(y=list(variables))
        .add(so.Line(linewidth=1.0), so.Agg(func="mean"))
    )

    if error_bar is not None:
        plot = plot.add(so.Band(alpha=0.15), so.Est(errorbar=error_bar))

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    (plot.scale(color=so.Nominal(palette, order=df[factor_name].cat.categories.tolist())).on(figure).plot(True))

    # Draw light/dark bands
    dark_band_spans = compute_dark_band_spans(
        datatable.dataset.light_cycles,
        datatable.dataset.experiment_started,
        df["Hours"].max(),
    )
    for band_start, band_end in dark_band_spans:
        for ax in figure.axes:
            ax.axvspan(band_start, band_end, color="gray", alpha=0.15)

    report = get_html_image_from_figure(figure)

    return DataPlotResult(
        report=report,
    )
