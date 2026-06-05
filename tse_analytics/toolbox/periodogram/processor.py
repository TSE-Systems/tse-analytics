from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class PeriodogramResult:
    report: str


def get_periodogram_result(
    datatable: Datatable,
    variable: Variable,
    factor_name: str,
    figsize: tuple[float, float] | None = None,
) -> PeriodogramResult:
    columns = datatable.get_default_columns() + list(datatable.dataset.factors) + [variable.name]
    df = datatable.get_filtered_df(columns)

    df = (
        df
        .groupby(factor_name, dropna=False, observed=False)
        .aggregate({
            "DateTime": "first",
            "Timedelta": "first",
            variable.name: "mean",
        })
        .reset_index()
    )

    df.dropna(inplace=True)

    t = df["DateTime"]
    y = df[variable.name]

    # Convert timestamps to numeric values (hours since start)
    reference_time = t.min()
    times_hours = [(ts - reference_time).total_seconds() / 3600 for ts in t]

    # Normalize activity for better analysis
    normalized_activity = (y - y.mean()) / y.std()

    # Define frequency grid (periods in hours)
    min_period = 1.0  # 1 hour
    max_period = 48.0  # 48 hours
    frequency = np.linspace(1 / max_period, 1 / min_period, 1000)

    # Calculate the periodogram
    power = LombScargle(times_hours, normalized_activity).power(frequency)

    # Convert frequency back to period in hours
    period = 1 / frequency

    # Get the most significant period
    strongest_period = period[np.argmax(power)]

    # Fold the data by the period
    phase = (np.array(times_hours) % strongest_period) / strongest_period
    phase_df = pd.DataFrame({"Phase": phase, variable.name: y})

    # Sort by phase for line plotting
    phase_df.sort_values("Phase", inplace=True)

    # Create the figure
    figure = plt.Figure(figsize=figsize, layout="tight")
    axs = figure.subplots(2, 1)

    axs[0].plot(period, power)
    axs[0].set(
        xlabel="Period (hours)",
        ylabel="Power",
        title=f"Lomb-Scargle Periodogram of {variable.name}. Strongest detected period: {strongest_period:.2f} hours",
    )

    # Add vertical lines at expected periods
    axs[0].axvline(x=24, color="r", linestyle="--", alpha=0.7, label="24h (Circadian)")
    axs[0].axvline(x=4, color="g", linestyle="--", alpha=0.7, label="4h (Ultradian)")
    axs[0].legend()

    axs[1].scatter(phase, y, alpha=0.5, marker=".")
    axs[1].plot(phase_df["Phase"], phase_df[variable.name], "r-", alpha=0.3)
    axs[1].set(
        xlabel=f"Phase (Period = {strongest_period:.2f} hours)",
        ylabel=variable.name,
        title="Phase-folded Data",
    )

    report = get_html_image_from_figure(figure)

    return PeriodogramResult(
        report=report,
    )
