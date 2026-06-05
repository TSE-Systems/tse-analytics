import math
from dataclasses import dataclass
from datetime import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_image_from_figure, time_to_float
from tse_analytics.core.utils.data import normalize_nd_array


def dataframe_to_actogram(
    df: pd.DataFrame,
    variable: Variable,
    bins_per_day: int = 24,
) -> tuple[np.ndarray, list]:
    """Convert a DataFrame with ``DateTime`` + activity into a ``(days, bins_per_day)`` array.

    Activity is aggregated per calendar day and per intra-day time bin using the
    variable's configured aggregation. Bins without samples are left at zero.
    """
    df = df.copy()

    # Calendar day and time-of-day (minutes since midnight).
    df["Date"] = df["DateTime"].dt.date.astype("datetime64[s]")
    df["Time"] = df["DateTime"].dt.hour * 60 + df["DateTime"].dt.minute.astype("Int64")

    # Intra-day bin index.
    minutes_per_bin = 24 * 60 / bins_per_day
    df["Bin"] = (df["Time"] / minutes_per_bin).astype("Int64")

    df = df.groupby(["Date", "Bin"], dropna=False, observed=False).aggregate({
        variable.name: variable.aggregation,
    })
    df.reset_index(inplace=True)

    # Unique, sorted recording days.
    unique_days = sorted(df["Date"].unique())

    # Scatter the aggregated values into a dense (days, bins) array (vectorized).
    activity_array = np.zeros((len(unique_days), bins_per_day), dtype=float)
    day_idx = pd.Index(unique_days).get_indexer(df["Date"])
    bin_idx = df["Bin"].to_numpy(dtype="int64", na_value=-1)
    values = df[variable.name].to_numpy(dtype=float, na_value=0.0)

    valid = (bin_idx >= 0) & (bin_idx < bins_per_day)
    activity_array[day_idx[valid], bin_idx[valid]] = values[valid]

    return activity_array, unique_days


def _draw_double_plotted_bars(
    ax,
    activity_data,
    binsize=None,
    highlight_periods=None,
    bar_color="black",
    day_labels=None,
):
    """Render double-plotted actogram bars, ticks and dark-period highlights into an existing Axes."""
    days_count, bins_per_day = activity_data.shape

    if day_labels is None:
        day_labels = [f"Day {i + 1}" for i in range(days_count)]

    time_labels = [f"{i}" for i in range(0, 26, 2)]
    xticks = np.linspace(0, bins_per_day, len(time_labels))

    if highlight_periods:
        for period in highlight_periods:
            start_bin = int(period["start"] / 24 * bins_per_day)
            end_bin = int(period["end"] / 24 * bins_per_day)
            ax.axvspan(start_bin, end_bin, color=period["color"], alpha=period.get("alpha", 0.2), zorder=1)
            ax.axvspan(
                start_bin + bins_per_day,
                end_bin + bins_per_day,
                color=period["color"],
                alpha=period.get("alpha", 0.2),
                zorder=1,
            )

    for i in range(days_count):
        if i > 0:
            ax.bar(
                np.arange(bins_per_day),
                activity_data[i - 1],
                width=1,
                color=bar_color,
                align="center",
                bottom=days_count - i,
                alpha=1,
                zorder=3,
                edgecolor="none",
            )
        ax.bar(
            np.arange(bins_per_day, 2 * bins_per_day),
            activity_data[i],
            width=1,
            color=bar_color,
            align="center",
            bottom=days_count - i,
            alpha=1,
            zorder=3,
            edgecolor="none",
        )

    ax.set_xticks(np.concatenate([xticks, xticks + bins_per_day]))
    ax.set_xticklabels(time_labels + time_labels)
    # Hide every other tick label
    [label.set_visible(False) for (i, label) in enumerate(ax.xaxis.get_ticklabels()) if i % 2 != 0]
    ax.set_yticks(np.arange(1, days_count + 1))
    ax.set_yticklabels(day_labels[::-1])

    ax.set_xlim(0, 2 * bins_per_day)
    ax.set_ylim(0, days_count + 1)

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Day")

    ax.axvline(bins_per_day, color="gray", linestyle="-", alpha=0.7, zorder=2)
    ax.grid(True, axis="x", alpha=0.3)


def plot_enhanced_actogram(
    activity_data,
    figsize: tuple[float, float] | None,
    days=None,
    binsize=None,
    title="Actogram",
    bar_color="black",
    highlight_periods=None,
):
    """
    Plot a more customized double-plotted actogram

    Parameters:
    -----------
    activity_data : array-like
        Activity data with shape (days, bins_per_day)
    days : list, optional
        List of day labels
    binsize : float, optional
        Size of each time bin in hours
    title : str
        Title of the plot
    bar_color : str
        Color of the activity bars
    highlight_periods : list of dict, optional
        List of periods to highlight, each with keys:
        - 'start': start hour (float)
        - 'end': end hour (float)
        - 'color': highlight color (str)
        - 'alpha': transparency (float)
    """
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()

    _draw_double_plotted_bars(
        ax,
        activity_data,
        binsize=binsize,
        highlight_periods=highlight_periods,
        bar_color=bar_color,
        day_labels=days,
    )
    ax.set_title(title)

    return figure, ax


def _build_actogram_periods(light_cycle_start: time, dark_cycle_start: time) -> list[dict]:
    if dark_cycle_start < light_cycle_start:
        return [
            {
                "start": time_to_float(dark_cycle_start),
                "end": time_to_float(light_cycle_start),
                "color": "gray",
                "alpha": 0.2,
            }
        ]
    return [
        {"start": 0.0, "end": time_to_float(light_cycle_start), "color": "gray", "alpha": 0.2},
        {"start": time_to_float(dark_cycle_start), "end": 24.0, "color": "gray", "alpha": 0.2},
    ]


# ---------------------------------------------------------------------------
# Combined actograms (multi-group)
# ---------------------------------------------------------------------------


def _collect_group_actograms(
    iter_df: pd.DataFrame,
    key_col: str,
    variable: Variable,
    bins_per_day: int,
) -> tuple[dict[str, np.ndarray], list]:
    """Build per-group double-plotted actogram arrays aligned to the union of dates.

    Each group's array is independently min-max normalized (matching the existing
    per-group actogram loop). Missing days are zero-filled so every group shares
    the same (n_days, bins_per_day) shape and can be rendered on a common axis.
    """
    raw: dict[str, tuple[np.ndarray, list]] = {}
    all_days: set = set()
    for label, g in iter_df.groupby(key_col, observed=True):
        activity_array, unique_days = dataframe_to_actogram(g, variable, bins_per_day)
        if activity_array.size == 0:
            continue
        if np.ptp(activity_array) > 0:
            activity_array = normalize_nd_array(activity_array)
        raw[str(label)] = (activity_array, unique_days)
        all_days.update(unique_days)

    shared_days = sorted(all_days)
    if not shared_days:
        return {}, []

    day_to_idx = {d: i for i, d in enumerate(shared_days)}
    n_days = len(shared_days)

    groups_data: dict[str, np.ndarray] = {}
    for label, (activity_array, unique_days) in raw.items():
        aligned = np.zeros((n_days, bins_per_day))
        for i, day in enumerate(unique_days):
            aligned[day_to_idx[day]] = activity_array[i]
        groups_data[label] = aligned

    return groups_data, shared_days


def plot_combined_actograms_grid(
    groups_data: dict[str, np.ndarray],
    shared_days: list,
    figsize: tuple[float, float] | None,
    binsize: float | None,
    highlight_periods: list | None,
    palette: dict[str, str] | None,
    title: str,
) -> plt.Figure:
    """2D grid of double-plotted actograms, one subplot per group."""
    n_groups = len(groups_data)
    base_w, base_h = figsize if figsize else (10.0, 6.0)
    if n_groups == 0:
        fig = plt.Figure(figsize=(base_w, base_h), layout="tight")
        fig.suptitle(title)
        return fig

    ncols = min(3, n_groups)
    nrows = math.ceil(n_groups / ncols)

    row_height = max(2.0, base_h * 0.55)
    grid_figsize = (base_w, min(row_height * nrows, 24.0))

    fig = plt.Figure(figsize=grid_figsize, layout="tight")
    axes_grid = fig.subplots(nrows, ncols, sharex=True, squeeze=False)
    flat_axes = axes_grid.flatten()

    day_labels = [d.strftime("%Y-%m-%d") for d in shared_days]

    for i, (label, activity_array) in enumerate(groups_data.items()):
        ax = flat_axes[i]
        color = (palette or {}).get(label, color_manager.get_color_hex(i))
        _draw_double_plotted_bars(
            ax,
            activity_array,
            binsize=binsize,
            highlight_periods=highlight_periods,
            bar_color=color,
            day_labels=day_labels,
        )
        ax.set_title(label)

    for j in range(n_groups, len(flat_axes)):
        flat_axes[j].axis("off")

    fig.suptitle(title)
    return fig


@dataclass
class ActogramResult:
    report: str


def get_actogram_result(
    datatable: Datatable,
    variable: Variable,
    bins_per_hour: int,
    figsize: tuple[float, float] | None = None,
) -> ActogramResult:
    columns = ["Animal", "DateTime", variable.name]
    df = datatable.get_filtered_df(columns)

    light_cycles = datatable.dataset.light_cycles
    periods = _build_actogram_periods(light_cycles.light_cycle_start, light_cycles.dark_cycle_start)

    bins_per_day = 24 * bins_per_hour

    # One double-plotted actogram per animal, aligned to a shared calendar axis.
    groups_data, shared_days = _collect_group_actograms(df, "Animal", variable, bins_per_day)

    if not groups_data:
        return ActogramResult(report="<p><em>No data available to plot the actogram.</em></p>")

    if len(groups_data) == 1:
        label, activity_array = next(iter(groups_data.items()))
        day_labels = [d.strftime("%Y-%m-%d") for d in shared_days]
        figure, _ = plot_enhanced_actogram(
            activity_array,
            figsize,
            day_labels,
            binsize=1 / bins_per_hour,
            highlight_periods=periods,
            bar_color=color_manager.get_color_hex(0),
            title=f"Actogram - {variable.name} ({label})",
        )
        report = get_html_image_from_figure(figure)
    else:
        figure = plot_combined_actograms_grid(
            groups_data,
            shared_days,
            figsize,
            binsize=1 / bins_per_hour,
            highlight_periods=periods,
            palette=None,
            title=f"Actogram - {variable.name}",
        )
        report = get_html_image_from_figure(figure)

    return ActogramResult(
        report=report,
    )
