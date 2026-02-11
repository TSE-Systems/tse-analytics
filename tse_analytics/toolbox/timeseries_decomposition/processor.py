from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.seasonal import STL, seasonal_decompose

from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class TimeseriesDecompositionResult:
    report: str


def get_timeseries_decomposition_result(
    df: pd.DataFrame,
    animal_id: str,
    variable: str,
    period: int,
    method: str,
    model: str,
    figsize: tuple[float, float] | None = None,
) -> TimeseriesDecompositionResult:
    index = pd.TimedeltaIndex(df["Timedelta"])
    df.set_index(index, inplace=True)

    # TODO: not sure interpolation should be used...
    df[variable] = df[variable].interpolate(limit_direction="both")

    match method:
        case "STL (smoothing)":
            result = STL(
                endog=df[variable],
                period=period,
            ).fit()
        case _:
            result = seasonal_decompose(
                df[variable],
                period=period,
                model=model,
                extrapolate_trend="freq",
            )

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")

    axs = figure.subplots(4, 1, sharex=True)
    figure.suptitle(f"Variable: {variable}. Animal: {animal_id}. Period: {period}")

    result.observed.plot(ax=axs[0], ylabel="Observed", lw=1)
    result.trend.plot(ax=axs[1], ylabel="Trend", lw=1)
    result.seasonal.plot(ax=axs[2], ylabel="Seasonal", lw=1)
    result.resid.plot(ax=axs[3], ylabel="Residual", lw=1, marker=".", markersize=2, linestyle="none")

    report = get_html_image_from_figure(figure)

    return TimeseriesDecompositionResult(
        report=report,
    )
