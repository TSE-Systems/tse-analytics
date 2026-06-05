from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class TimeseriesAutocorrelationResult:
    report: str


def get_timeseries_autocorrelation_result(
    datatable: Datatable,
    animal_id: str,
    variable_name: str,
    figsize: tuple[float, float] | None = None,
) -> TimeseriesAutocorrelationResult:
    columns = ["DateTime", "Timedelta", "Animal", variable_name]
    df = datatable.get_filtered_df(columns)
    df = df[df["Animal"] == animal_id]
    df.reset_index(drop=True, inplace=True)

    index = pd.DatetimeIndex(df["DateTime"])
    df.set_index(index, inplace=True)

    df[variable_name] = df[variable_name].interpolate(limit_direction="both")

    # Create a figure with a tight layout
    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = plt.Figure(figsize=figsize, layout="tight")

    axs = figure.subplots(2, 1, sharex=True)
    figure.suptitle(f"Timeseries autocorrelation of {variable_name} for animal {animal_id}")

    plot_acf(df[variable_name], ax=axs[0], adjusted=False, title="Autocorrelation")
    axs[0].set_ylabel(variable_name)
    plot_pacf(df[variable_name], ax=axs[1], title="Partial Autocorrelation")
    axs[1].set_ylabel(variable_name)

    report = get_html_image_from_figure(figure)

    return TimeseriesAutocorrelationResult(
        report=report,
    )
