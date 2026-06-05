from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure
from tse_analytics.toolbox.chronobiology.processor import _lombscargle_period, _to_hours_since_start

# Period search grid (hours). The frequency grid is uniformly spaced in frequency
# between 1 / MAX_PERIOD_HOURS and 1 / MIN_PERIOD_HOURS.
MIN_PERIOD_HOURS = 1.0
MAX_PERIOD_HOURS = 48.0
N_FREQUENCIES = 1000


@dataclass
class PeriodogramResult:
    report: str
    # Dominant (highest-power) period in hours per group level; NaN where the
    # series was too short or constant. Exposed for testing and reuse.
    dominant_periods: dict[str, float] = field(default_factory=dict)


def _plot_periodogram(
    series: dict[str, tuple[np.ndarray, np.ndarray, float]],
    variable: Variable,
    palette: dict[str, str],
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    """Overlay one Lomb–Scargle power curve per group level on a single axis."""
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    plotted = False
    for i, (label, (period, power, _dominant)) in enumerate(series.items()):
        if period.size == 0:
            continue
        color = palette.get(label, color_manager.get_color_hex(i))
        ax.plot(period, power, label=label, color=color, alpha=0.8)
        plotted = True
    ax.axvline(x=24, color="red", linestyle="--", alpha=0.7, label="24 h (circadian)")
    ax.set_xlabel("Period (hours)")
    ax.set_ylabel("Lomb–Scargle power")
    ax.set_title(f"Lomb–Scargle periodogram — {variable.name}")
    if plotted:
        ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def get_periodogram_result(
    datatable: Datatable,
    variable: Variable,
    factor_name: str,
    min_period: float = MIN_PERIOD_HOURS,
    max_period: float = MAX_PERIOD_HOURS,
    figsize: tuple[float, float] | None = None,
) -> PeriodogramResult:
    """Compute a Lomb–Scargle periodogram of ``variable``, one series per group level.

    Each factor level's mean time series is analysed independently; the resulting
    power spectra are overlaid and the dominant period per group is tabulated.
    """
    dataset = datatable.dataset

    if "DateTime" not in datatable.df.columns:
        return PeriodogramResult(
            report="<p><em>DateTime column not available — the periodogram requires a time series.</em></p>"
        )

    # De-duplicate columns: "Animal" is both a default column and a factor.
    wanted = ["DateTime", "Animal", factor_name, variable.name]
    columns = list(dict.fromkeys(c for c in wanted if c in datatable.df.columns))
    df = datatable.get_filtered_df(columns).dropna()

    if df.empty:
        return PeriodogramResult(report="<p><em>No data available to compute the periodogram.</em></p>")

    # Per-group-level mean time series (one series per factor level). Grouping by
    # "Animal" already yields one series per animal, so no aggregation is needed.
    if factor_name != "Animal":
        grouped_df = (
            df
            .groupby([factor_name, "DateTime"], dropna=False, observed=False)
            .aggregate({variable.name: "mean"})
            .reset_index()
        )
    else:
        grouped_df = df

    # The Lomb–Scargle power spectrum is invariant to a constant time offset, so a
    # shared reference is fine and keeps per-group x-axes comparable.
    reference_time = grouped_df["DateTime"].min()

    palette = (
        color_manager.get_level_to_color_dict(dataset.factors[factor_name]) if factor_name in dataset.factors else {}
    )
    if not isinstance(palette, dict):
        palette = {}

    ls_series: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    dominant_periods: dict[str, float] = {}
    table_rows: list[dict] = []
    for label, g in grouped_df.groupby(factor_name, observed=True):
        label = str(label)
        t = _to_hours_since_start(g["DateTime"], reference_time)
        y = g[variable.name].to_numpy(dtype=float)
        period, power, dominant = _lombscargle_period(t, y, min_period, max_period, N_FREQUENCIES)
        ls_series[label] = (period, power, dominant)
        dominant_periods[label] = dominant
        table_rows.append({
            "Group": label,
            "N samples": int(len(g)),
            "Dominant period (h)": dominant,
        })

    if all(period.size == 0 for period, _power, _dominant in ls_series.values()):
        return PeriodogramResult(
            report=(
                "<p><em>Not enough valid data to compute the periodogram "
                "(each series needs ≥ 4 samples and a non-constant signal).</em></p>"
            ),
            dominant_periods=dominant_periods,
        )

    sections = [
        get_html_image_from_figure(_plot_periodogram(ls_series, variable, palette, figsize)),
        get_great_table(pd.DataFrame(table_rows), "Dominant period per group").as_raw_html(inline_css=True),
    ]
    return PeriodogramResult(
        report="\n<p>\n".join(sections),
        dominant_periods=dominant_periods,
    )
