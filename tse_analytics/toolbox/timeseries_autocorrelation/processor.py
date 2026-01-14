from dataclasses import dataclass

import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class TimeseriesAutocorrelationResult:
    report: str


def get_timeseries_autocorrelation_result(
    df: pd.DataFrame,
    animal_id: str,
    variable: str,
    figsize: tuple[float, float] | None = None,
) -> TimeseriesAutocorrelationResult:
    index = pd.DatetimeIndex(df["DateTime"])
    df.set_index(index, inplace=True)

    df[variable] = df[variable].interpolate(limit_direction="both")

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")

    axs = figure.subplots(2, 1, sharex=True)
    figure.suptitle(f"Timeseries autocorrelation of {variable} for animal {animal_id}")

    plot_acf(df[variable], ax=axs[0], adjusted=False, title="Autocorrelation")
    axs[0].set_ylabel(variable)
    plot_pacf(df[variable], ax=axs[1], title="Partial Autocorrelation")
    axs[1].set_ylabel(variable)

    report = get_html_image_from_figure(figure)

    return TimeseriesAutocorrelationResult(
        report=report,
    )
