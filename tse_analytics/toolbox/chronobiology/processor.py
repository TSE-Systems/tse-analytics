"""Chronobiology analysis report.

Composes a multi-section HTML report combining zeitgeber-time conversion,
Lomb-Scargle period detection, single-component cosinor, activity onset/offset
detection, a double-plotted actogram.
"""

import math
from dataclasses import dataclass
from datetime import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle
from scipy.stats import f as f_dist

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.operators.group_by_pipe_operator import group_by_columns
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import (
    get_great_table,
    get_html_image_from_figure,
    time_to_float,
)
from tse_analytics.core.utils.data import normalize_nd_array
from tse_analytics.toolbox.actogram.processor import (
    _draw_double_plotted_bars,
    dataframe_to_actogram,
    plot_enhanced_actogram,
)


@dataclass
class ChronobiologyResult:
    report: str


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def _compute_zeitgeber_time(dt: pd.Series, light_cycle_start: time) -> pd.Series:
    """Zeitgeber time in hours, ZT 0 = lights on, wrapped to [0, 24)."""
    sec_of_day = dt.dt.hour * 3600 + dt.dt.minute * 60 + dt.dt.second
    ls_seconds = light_cycle_start.hour * 3600 + light_cycle_start.minute * 60 + light_cycle_start.second
    return ((sec_of_day - ls_seconds) % 86400) / 3600.0


def _to_hours_since_start(dt: pd.Series, reference: pd.Timestamp) -> np.ndarray:
    return ((dt - reference).dt.total_seconds() / 3600.0).to_numpy(dtype=float)


def _fit_cosinor(t_hours: np.ndarray, y: np.ndarray, period_hours: float = 24.0) -> dict[str, float]:
    """Single-component cosinor via OLS on the [1, cos(ωt), sin(ωt)] design.

    Returns MESOR, amplitude, acrophase (hours), percent rhythm (R²), and an
    F-test p-value vs. the intercept-only model. NaNs are returned when the
    series is degenerate.
    """
    t = np.asarray(t_hours, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    n = t.size
    if n < 4 or np.ptp(y) == 0:
        return {
            "MESOR": float("nan"),
            "Amplitude": float("nan"),
            "Acrophase_h": float("nan"),
            "PR": float("nan"),
            "p_value": float("nan"),
            "N": float(n),
        }

    omega = 2 * np.pi / period_hours
    x = np.column_stack([np.ones_like(t), np.cos(omega * t), np.sin(omega * t)])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    mesor, beta, gamma = coeffs
    amplitude = float(np.hypot(beta, gamma))
    phi = float(np.arctan2(-gamma, beta))
    acrophase_hours = float((-phi / omega) % period_hours)

    y_pred = x @ coeffs
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # F-test vs intercept-only (df1=2, df2=n-3).
    if n > 3 and ss_res > 0:
        f_stat = ((ss_tot - ss_res) / 2.0) / (ss_res / (n - 3))
        p_value = float(f_dist.sf(f_stat, 2, n - 3))
    else:
        p_value = float("nan")

    return {
        "MESOR": float(mesor),
        "Amplitude": amplitude,
        "Acrophase_h": acrophase_hours,
        "PR": float(r2),
        "p_value": p_value,
        "N": float(n),
    }


def _fit_two_component_cosinor(
    t_hours: np.ndarray,
    y: np.ndarray,
    period1_hours: float = 24.0,
    period2_hours: float = 12.0,
) -> dict[str, float]:
    """Two-component cosinor via OLS on [1, cos(ω₁t), sin(ω₁t), cos(ω₂t), sin(ω₂t)].

    Returns MESOR, amplitude/acrophase per component, combined percent
    rhythm (R²), and an F-test p-value vs. the intercept-only model
    (df1=4, df2=n-5). NaNs on degenerate series.
    """
    t = np.asarray(t_hours, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    n = t.size
    nan_result = {
        "MESOR": float("nan"),
        "Amplitude_1": float("nan"),
        "Acrophase_1_h": float("nan"),
        "Amplitude_2": float("nan"),
        "Acrophase_2_h": float("nan"),
        "PR": float("nan"),
        "p_value": float("nan"),
        "N": float(n),
    }
    if n < 6 or np.ptp(y) == 0 or period1_hours <= 0 or period2_hours <= 0:
        return nan_result

    omega1 = 2 * np.pi / period1_hours
    omega2 = 2 * np.pi / period2_hours
    x = np.column_stack([
        np.ones_like(t),
        np.cos(omega1 * t),
        np.sin(omega1 * t),
        np.cos(omega2 * t),
        np.sin(omega2 * t),
    ])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    mesor, b1, g1, b2, g2 = coeffs

    amp1 = float(np.hypot(b1, g1))
    amp2 = float(np.hypot(b2, g2))
    acro1 = float((-np.arctan2(-g1, b1) / omega1) % period1_hours)
    acro2 = float((-np.arctan2(-g2, b2) / omega2) % period2_hours)

    y_pred = x @ coeffs
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    if n > 5 and ss_res > 0:
        f_stat = ((ss_tot - ss_res) / 4.0) / (ss_res / (n - 5))
        p_value = float(f_dist.sf(f_stat, 4, n - 5))
    else:
        p_value = float("nan")

    return {
        "MESOR": float(mesor),
        "Amplitude_1": amp1,
        "Acrophase_1_h": acro1,
        "Amplitude_2": amp2,
        "Acrophase_2_h": acro2,
        "PR": float(r2),
        "p_value": p_value,
        "N": float(n),
    }


def _lombscargle_period(
    t_hours: np.ndarray,
    y: np.ndarray,
    min_period: float = 1.0,
    max_period: float = 48.0,
    n_frequencies: int = 1000,
) -> tuple[np.ndarray, np.ndarray, float]:
    t = np.asarray(t_hours, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    if t.size < 4 or np.std(y) == 0:
        return np.array([]), np.array([]), float("nan")

    frequency = np.linspace(1.0 / max_period, 1.0 / min_period, n_frequencies)
    y_norm = (y - y.mean()) / y.std()
    power = LombScargle(t, y_norm).power(frequency)
    period = 1.0 / frequency
    return period, power, float(period[int(np.argmax(power))])


def _detect_onset_offset(
    df_animal: pd.DataFrame,
    variable_name: str,
    threshold_pct: float,
) -> pd.DataFrame:
    """Per-day onset/offset times using a per-day percentile threshold."""
    df_animal = df_animal[["DateTime", variable_name]].dropna().copy()
    df_animal["Date"] = df_animal["DateTime"].dt.date
    rows: list[dict] = []
    for date, group in df_animal.groupby("Date", sort=True):
        if group[variable_name].nunique() < 2:
            continue
        threshold = float(np.nanpercentile(group[variable_name].to_numpy(), threshold_pct))
        above = group[group[variable_name] >= threshold]
        if above.empty:
            continue
        onset = above["DateTime"].iloc[0]
        offset = above["DateTime"].iloc[-1]
        rows.append({
            "Date": str(date),
            "Onset": onset.strftime("%H:%M"),
            "Offset": offset.strftime("%H:%M"),
            "Alpha_h": (offset - onset).total_seconds() / 3600.0,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Section plots
# ---------------------------------------------------------------------------


def _plot_zt_profile(
    df: pd.DataFrame,
    variable: Variable,
    light_cycle_start: time,
    group_col: str | None,
    palette: dict[str, str] | dict[int, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    df = df.copy()
    df["ZT"] = _compute_zeitgeber_time(df["DateTime"], light_cycle_start)
    df["ZT_bin"] = df["ZT"].round().astype("Int64") % 24

    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()

    if group_col in df.columns:
        for i, (level, g) in enumerate(df.groupby(group_col, observed=True)):
            agg = g.groupby("ZT_bin", observed=True)[variable.name].agg(["mean", "sem"]).reset_index()
            color = (palette or {}).get(str(level), color_manager.get_color_hex(i))
            ax.plot(agg["ZT_bin"], agg["mean"], label=str(level), color=color)
            ax.fill_between(agg["ZT_bin"], agg["mean"] - agg["sem"], agg["mean"] + agg["sem"], alpha=0.2, color=color)
        ax.legend(title=group_col)
    else:
        agg = df.groupby("ZT_bin", observed=True)[variable.name].agg(["mean", "sem"]).reset_index()
        color = color_manager.get_color_hex(0)
        ax.plot(agg["ZT_bin"], agg["mean"], color=color)
        ax.fill_between(agg["ZT_bin"], agg["mean"] - agg["sem"], agg["mean"] + agg["sem"], alpha=0.2, color=color)

    ax.axvspan(12, 24, color="gray", alpha=0.15, zorder=0)
    ax.set_xlabel("Zeitgeber time (h)")
    ax.set_ylabel(f"{variable.name} ({variable.unit})" if variable.unit else variable.name)
    ax.set_title(f"Zeitgeber-time profile — {variable.name}")
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 4))
    ax.grid(True, alpha=0.3)
    return figure


def _plot_periodogram(
    series: dict[str, tuple[np.ndarray, np.ndarray, float]],
    variable: Variable,
    palette: dict[str, str] | dict[int, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    for i, (label, (period, power, _dom)) in enumerate(series.items()):
        if period.size == 0:
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        ax.plot(period, power, label=label, color=color, alpha=0.8)
    ax.axvline(x=24, color="red", linestyle="--", alpha=0.7, label="24 h")
    ax.set_xlabel("Period (hours)")
    ax.set_ylabel("Lomb–Scargle power")
    ax.set_title(f"Lomb–Scargle periodogram — {variable.name}")
    ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def _plot_cosinor_fits(
    fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]],
    variable: Variable,
    period_hours: float,
    palette: dict[str, str] | dict[int, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    omega = 2 * np.pi / period_hours
    for i, (label, (t, y, params)) in enumerate(fits.items()):
        if not np.isfinite(params.get("MESOR", np.nan)):
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        phase = t % period_hours
        order = np.argsort(phase)
        ax.scatter(phase, y, alpha=0.25, s=8, color=color)
        t_grid = np.linspace(0, period_hours, 200)
        y_fit = params["MESOR"] + params["Amplitude"] * np.cos(omega * t_grid - omega * params["Acrophase_h"])
        ax.plot(
            t_grid, y_fit, color=color, label=f"{label} (A={params['Amplitude']:.2f}, φ={params['Acrophase_h']:.1f} h)"
        )
        _ = order  # (phase ordering retained for potential line overlay)
    ax.set_xlabel(f"Phase within {period_hours:g}-h period")
    ax.set_ylabel(f"{variable.name} ({variable.unit})" if variable.unit else variable.name)
    ax.set_title(f"Cosinor fits — {variable.name}")
    ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def _plot_two_component_fits(
    fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]],
    variable: Variable,
    period1_hours: float,
    period2_hours: float,
    palette: dict[str, str] | dict[int, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    omega1 = 2 * np.pi / period1_hours
    omega2 = 2 * np.pi / period2_hours
    for i, (label, (t, y, params)) in enumerate(fits.items()):
        if not np.isfinite(params.get("MESOR", np.nan)):
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        phase = t % period1_hours
        ax.scatter(phase, y, alpha=0.25, s=8, color=color)
        t_grid = np.linspace(0, period1_hours, 400)
        y_fit = (
            params["MESOR"]
            + params["Amplitude_1"] * np.cos(omega1 * t_grid - omega1 * params["Acrophase_1_h"])
            + params["Amplitude_2"] * np.cos(omega2 * t_grid - omega2 * params["Acrophase_2_h"])
        )
        ax.plot(
            t_grid,
            y_fit,
            color=color,
            label=f"{label} (A₁={params['Amplitude_1']:.2f}, A₂={params['Amplitude_2']:.2f})",
        )
    ax.set_xlabel(f"Phase within {period1_hours:g}-h period")
    ax.set_ylabel(f"{variable.name} ({variable.unit})" if variable.unit else variable.name)
    ax.set_title(f"Two-component cosinor fits — {variable.name}")
    ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def _plot_onset_offset(
    onsets: dict[str, pd.DataFrame],
    palette: dict[str, str] | dict[int, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    for i, (label, df) in enumerate(onsets.items()):
        if df.empty:
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        onset_h = (
            pd.to_datetime(df["Onset"], format="%H:%M").dt.hour
            + pd.to_datetime(df["Onset"], format="%H:%M").dt.minute / 60.0
        )
        offset_h = (
            pd.to_datetime(df["Offset"], format="%H:%M").dt.hour
            + pd.to_datetime(df["Offset"], format="%H:%M").dt.minute / 60.0
        )
        days = np.arange(1, len(df) + 1)
        ax.plot(onset_h, days, marker="o", linestyle="-", color=color, label=f"{label} onset")
        ax.plot(offset_h, days, marker="s", linestyle="--", color=color, label=f"{label} offset")
    ax.set_xlabel("Clock time (h)")
    ax.set_ylabel("Day")
    ax.set_title("Activity onset / offset per day")
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(fontsize="small", ncol=2)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    return figure


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
# Orchestrator
# ---------------------------------------------------------------------------


def _resolve_group_column(grouping_settings: GroupingSettings) -> str | None:
    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            return "Animal"
        case GroupingMode.FACTOR:
            return grouping_settings.factor_name
        case GroupingMode.RUN:
            return "Run"


def _resolve_palette(
    datatable: Datatable,
    grouping_settings: GroupingSettings,
) -> dict[str, str] | dict[int, str] | None:
    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            return color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.FACTOR:
            return color_manager.get_level_to_color_dict(datatable.dataset.factors[grouping_settings.factor_name])
        case GroupingMode.RUN:
            return color_manager.get_run_to_color_dict(datatable.dataset.runs)


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


def get_chronobiology_result(
    datatable: Datatable,
    variable: Variable,
    grouping_settings: GroupingSettings,
    period_hours: float = 24.0,
    period2_hours: float = 12.0,
    bins_per_hour: int = 6,
    onset_threshold_pct: float = 50.0,
    figsize: tuple[float, float] | None = None,
) -> ChronobiologyResult:
    columns = datatable.get_default_columns() + list(datatable.dataset.factors) + [variable.name]
    df = datatable.get_filtered_df(columns)
    df = df.dropna()

    dataset = datatable.dataset
    time_cycles = dataset.light_cycles
    light_cycle_start = time_cycles.light_cycle_start
    dark_cycle_start = time_cycles.dark_cycle_start

    has_datetime = "DateTime" in df.columns
    sections: list[str] = []

    # --- Section 1: summary table -----------------------------------------
    sample_interval = datatable.sample_interval
    if sample_interval is None and has_datetime and len(df) > 1:
        sample_interval = df["DateTime"].diff().median()
    n_animals = df["Animal"].nunique() if "Animal" in df.columns else 0
    if has_datetime:
        date_min = df["DateTime"].min()
        date_max = df["DateTime"].max()
        duration: pd.Timedelta | None = date_max - date_min
    else:
        date_min = None
        date_max = None
        duration = None

    summary_df = pd.DataFrame([
        {
            "Variable": variable.name,
            "Unit": variable.unit or "",
            "Animals (N)": n_animals,
            "Start": str(date_min) if date_min is not None else "—",
            "End": str(date_max) if date_max is not None else "—",
            "Duration": str(duration) if duration is not None else "—",
            "Sample interval": str(sample_interval) if sample_interval is not None else "—",
            "Light cycle start": light_cycle_start.strftime("%H:%M"),
            "Dark cycle start": dark_cycle_start.strftime("%H:%M"),
            "Cosinor period (h)": f"{period_hours:g}",
            "Harmonic period (h)": f"{period2_hours:g}",
            "Group by": grouping_settings.mode.value
            + (f" ({grouping_settings.factor_name})" if grouping_settings.mode == GroupingMode.FACTOR else ""),
        }
    ])
    sections.append(
        get_great_table(
            summary_df.T.reset_index().rename(columns={"index": "Field", 0: "Value"}), "Summary"
        ).as_raw_html(inline_css=True)
    )

    if not has_datetime:
        sections.append("<p><em>DateTime column not available — time-series sections skipped.</em></p>")
        return ChronobiologyResult(report="\n<p>\n".join(sections))

    # Common reference and group column resolution -------------------------
    reference_time = datatable.dataset.experiment_started
    group_col = _resolve_group_column(grouping_settings)
    palette = _resolve_palette(datatable, grouping_settings)

    # Build grouped df for visualisations (ZT profile / actogram) ----------
    grouped_df = group_by_columns(df.copy(), {variable.name: variable}, grouping_settings)

    # --- Section 2: ZT profile --------------------------------------------
    sections.append("<h3>Zeitgeber-time profile</h3>")
    sections.append(
        get_html_image_from_figure(
            _plot_zt_profile(grouped_df, variable, light_cycle_start, group_col, palette, figsize)
        )
    )

    # --- Section 3: Lomb–Scargle periodogram ------------------------------
    # Iterate over animals (ANIMAL mode) or group levels (everything else).
    ls_series: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    ls_table_rows: list[dict] = []
    if grouping_settings.mode == GroupingMode.ANIMAL:
        iter_df = df
        key_col = "Animal"
    else:
        iter_df = grouped_df
        key_col = group_col if group_col and group_col in grouped_df.columns else None

    if key_col is None:
        t = _to_hours_since_start(iter_df["DateTime"], reference_time)
        y = iter_df[variable.name].to_numpy(dtype=float)
        period, power, dominant = _lombscargle_period(t, y)
        ls_series["Total"] = (period, power, dominant)
        ls_table_rows.append({"Group": "Total", "Dominant period (h)": dominant, "N samples": int(t.size)})
    else:
        for label, g in iter_df.groupby(key_col, observed=True):
            t = _to_hours_since_start(g["DateTime"], reference_time)
            y = g[variable.name].to_numpy(dtype=float)
            period, power, dominant = _lombscargle_period(t, y)
            ls_series[str(label)] = (period, power, dominant)
            ls_table_rows.append({"Group": str(label), "Dominant period (h)": dominant, "N samples": int(t.size)})

    sections.append("<h3>Lomb–Scargle periodogram</h3>")
    sections.append(get_html_image_from_figure(_plot_periodogram(ls_series, variable, palette, figsize)))
    sections.append(get_great_table(pd.DataFrame(ls_table_rows), "Dominant periods").as_raw_html(inline_css=True))

    # --- Section 4: single-component cosinor ------------------------------
    cosinor_rows: list[dict] = []
    cosinor_fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]] = {}
    if key_col is None:
        t = _to_hours_since_start(iter_df["DateTime"], reference_time)
        y = iter_df[variable.name].to_numpy(dtype=float)
        params = _fit_cosinor(t, y, period_hours)
        cosinor_fits["Total"] = (t, y, params)
        cosinor_rows.append({"Group": "Total", **params})
    else:
        for label, g in iter_df.groupby(key_col, observed=True):
            t = _to_hours_since_start(g["DateTime"], reference_time)
            y = g[variable.name].to_numpy(dtype=float)
            params = _fit_cosinor(t, y, period_hours)
            cosinor_fits[str(label)] = (t, y, params)
            cosinor_rows.append({"Group": str(label), **params})

    sections.append(f"<h3>Single-component cosinor (period = {period_hours:g} h)</h3>")
    sections.append(get_great_table(pd.DataFrame(cosinor_rows), "Cosinor parameters").as_raw_html(inline_css=True))
    sections.append(
        get_html_image_from_figure(_plot_cosinor_fits(cosinor_fits, variable, period_hours, palette, figsize))
    )

    # --- Section 4b: two-component cosinor --------------------------------
    two_comp_rows: list[dict] = []
    two_comp_fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]] = {}
    if key_col is None:
        t = _to_hours_since_start(iter_df["DateTime"], reference_time)
        y = iter_df[variable.name].to_numpy(dtype=float)
        params = _fit_two_component_cosinor(t, y, period_hours, period2_hours)
        two_comp_fits["Total"] = (t, y, params)
        two_comp_rows.append({"Group": "Total", **params})
    else:
        for label, g in iter_df.groupby(key_col, observed=True):
            t = _to_hours_since_start(g["DateTime"], reference_time)
            y = g[variable.name].to_numpy(dtype=float)
            params = _fit_two_component_cosinor(t, y, period_hours, period2_hours)
            two_comp_fits[str(label)] = (t, y, params)
            two_comp_rows.append({"Group": str(label), **params})

    sections.append(f"<h3>Two-component cosinor (periods = {period_hours:g} h + {period2_hours:g} h)</h3>")
    sections.append(
        get_great_table(pd.DataFrame(two_comp_rows), "Two-component cosinor parameters").as_raw_html(inline_css=True)
    )
    sections.append(
        get_html_image_from_figure(
            _plot_two_component_fits(two_comp_fits, variable, period_hours, period2_hours, palette, figsize)
        )
    )

    # --- Section 5: activity onset / offset -------------------------------
    onset_tables: dict[str, pd.DataFrame] = {}
    onset_combined_rows: list[dict] = []
    if grouping_settings.mode == GroupingMode.ANIMAL:
        for animal, g in df.groupby("Animal", observed=True):
            table = _detect_onset_offset(g, variable.name, onset_threshold_pct)
            if not table.empty:
                onset_tables[str(animal)] = table
                for _, row in table.iterrows():
                    onset_combined_rows.append({"Animal": str(animal), **row.to_dict()})
    elif key_col is not None:
        for label, g in grouped_df.groupby(key_col, observed=True):
            table = _detect_onset_offset(g, variable.name, onset_threshold_pct)
            if not table.empty:
                onset_tables[str(label)] = table
                for _, row in table.iterrows():
                    onset_combined_rows.append({key_col: str(label), **row.to_dict()})
    else:
        table = _detect_onset_offset(grouped_df, variable.name, onset_threshold_pct)
        if not table.empty:
            onset_tables["Total"] = table
            for _, row in table.iterrows():
                onset_combined_rows.append({"Group": "Total", **row.to_dict()})

    sections.append(f"<h3>Activity onset / offset (threshold = {onset_threshold_pct:g}th percentile)</h3>")
    if onset_combined_rows:
        sections.append(
            get_great_table(pd.DataFrame(onset_combined_rows), "Daily onset / offset").as_raw_html(inline_css=True)
        )
        sections.append(get_html_image_from_figure(_plot_onset_offset(onset_tables, palette, figsize)))
    else:
        sections.append("<p><em>Not enough data to detect daily onset / offset.</em></p>")

    # --- Section 6: double-plotted actogram -------------------------------
    if duration is None or duration < pd.Timedelta(hours=48):
        sections.append("<p><em>Experiment shorter than 48 h — actogram skipped.</em></p>")
    else:
        periods = _build_actogram_periods(light_cycle_start, dark_cycle_start)
        bins_per_day = 24 * bins_per_hour
        if key_col is None:
            activity_array, unique_days = dataframe_to_actogram(grouped_df, variable, bins_per_day)
            if activity_array.size and np.ptp(activity_array) > 0:
                activity_array = normalize_nd_array(activity_array)
            figure, _ = plot_enhanced_actogram(
                activity_array,
                figsize,
                [d.strftime("%Y-%m-%d") for d in unique_days],
                binsize=1 / bins_per_hour,
                highlight_periods=periods,
                bar_color=color_manager.get_color_hex(0),
                title=f"Actogram — {variable.name} (Total)",
            )
            sections.append(get_html_image_from_figure(figure))
        else:
            groups_data, shared_days = _collect_group_actograms(iter_df, key_col, variable, bins_per_day)
            if len(groups_data) >= 2:
                sections.append(
                    get_html_image_from_figure(
                        plot_combined_actograms_grid(
                            groups_data,
                            shared_days,
                            figsize,
                            binsize=1 / bins_per_hour,
                            highlight_periods=periods,
                            palette=palette,
                            title=f"Actograms grid — {variable.name}",
                        )
                    )
                )

    report = "\n<p>\n".join(sections)
    return ChronobiologyResult(report=report)
