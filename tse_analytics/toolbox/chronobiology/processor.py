"""Chronobiology analysis report.

Composes a multi-section HTML report combining zeitgeber-time conversion,
Lomb-Scargle period detection, single-component cosinor, activity onset/offset
detection, a double-plotted actogram.

Statistics notes
----------------
- Cosinor fits use ordinary least squares on a ``[1, cos(ωt), sin(ωt)]`` design.
  The reported single-component parameters are aggregated **per animal** within
  each group (mean ± SEM, circular mean for acrophase), which is the more
  defensible level of inference than a single fit on the pooled/averaged series.
- The per-fit F-test p-value assumes independent residuals and is therefore
  anti-conservative for serially-correlated time series; treat it as a screening
  statistic and rely on the between-animal aggregation.
- Acrophases and activity onset/offset are reported in **Zeitgeber time (ZT)**
  (ZT 0 = lights on) for biological interpretability.
"""

import math
from dataclasses import dataclass, field
from datetime import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle
from scipy.stats import f as f_dist

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import (
    get_great_table,
    get_html_image_from_figure,
    time_to_float,
)
from tse_analytics.toolbox.actogram.processor import (
    _build_actogram_periods,
    _collect_group_actograms,
    plot_combined_actograms_grid,
    plot_enhanced_actogram,
)


@dataclass
class ResultTable:
    """A chronobiology result table that can be materialized as a dataset ``Datatable``.

    ``id_column`` is the non-variable identifier column: ``"Animal"`` for the per-animal
    parameter table, or the group-by factor name for the per-group summary tables.
    """

    df: pd.DataFrame
    id_column: str

    def to_datatable(self, dataset: Dataset, name: str) -> Datatable:
        """Build a dataset ``Datatable`` from this result table.

        Numeric columns (other than ``id_column``) become ``Variable`` metadata so the
        table can be used in further analyses (e.g. ANOVA). Dataset factors are attached
        via ``set_factors`` — a no-op unless the table has an ``"Animal"`` column.
        """
        return Datatable.from_dataframe(
            dataset,
            name,
            self.df,
            origin="Chronobiology",
            description=f"Chronobiology result: {name}",
            id_column=self.id_column,
        )


@dataclass
class ChronobiologyResult:
    report: str
    tables: dict[str, ResultTable] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def _compute_zeitgeber_time(dt: pd.Series, light_cycle_start: time) -> pd.Series:
    """Zeitgeber time in hours, ZT 0 = lights on, wrapped to [0, 24)."""
    sec_of_day = dt.dt.hour * 3600 + dt.dt.minute * 60 + dt.dt.second
    ls_seconds = light_cycle_start.hour * 3600 + light_cycle_start.minute * 60 + light_cycle_start.second
    return ((sec_of_day - ls_seconds) % 86400) / 3600.0


def _zeitgeber_offset(reference: pd.Timestamp, light_cycle_start: time) -> float:
    """Zeitgeber time (hours) of a single timestamp — the ZT of elapsed-hour 0."""
    sec_of_day = reference.hour * 3600 + reference.minute * 60 + reference.second
    ls_seconds = light_cycle_start.hour * 3600 + light_cycle_start.minute * 60 + light_cycle_start.second
    return ((sec_of_day - ls_seconds) % 86400) / 3600.0


def _to_hours_since_start(dt: pd.Series, reference: pd.Timestamp) -> np.ndarray:
    return ((dt - reference).dt.total_seconds() / 3600.0).to_numpy(dtype=float)


def _sem(values: np.ndarray) -> float:
    """Standard error of the mean; 0.0 for a single value, NaN for none."""
    n = values.size
    if n == 0:
        return float("nan")
    if n == 1:
        return 0.0
    return float(np.std(values, ddof=1) / math.sqrt(n))


def _circular_mean_hours(hours: np.ndarray, period_hours: float) -> float:
    """Circular mean of phase values expressed in hours within ``period_hours``."""
    hours = np.asarray(hours, dtype=float)
    hours = hours[np.isfinite(hours)]
    if hours.size == 0 or period_hours <= 0:
        return float("nan")
    angles = 2 * np.pi * hours / period_hours
    mean_angle = math.atan2(float(np.mean(np.sin(angles))), float(np.mean(np.cos(angles))))
    return float((mean_angle * period_hours / (2 * np.pi)) % period_hours)


def _fit_cosinor(t_hours: np.ndarray, y: np.ndarray, period_hours: float = 24.0) -> dict[str, float]:
    """Single-component cosinor via OLS on the [1, cos(ωt), sin(ωt)] design.

    Returns MESOR, amplitude, acrophase (elapsed hours), percent rhythm (R²),
    and an F-test p-value vs. the intercept-only model. NaNs are returned when
    the series is degenerate.
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

    Returns MESOR, amplitude/acrophase per component (elapsed hours), combined
    percent rhythm (R²), and an F-test p-value vs. the intercept-only model
    (df1=4, df2=n-5). NaNs on degenerate series (including equal periods, which
    make the design matrix singular).
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
    if n < 6 or np.ptp(y) == 0 or period1_hours <= 0 or period2_hours <= 0 or period1_hours == period2_hours:
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


def _per_animal_fits(
    group_df: pd.DataFrame,
    variable_name: str,
    reference: pd.Timestamp,
    period_hours: float,
) -> tuple[list[dict[str, float]], list[float]]:
    """Fit a single-component cosinor and Lomb-Scargle period for each animal.

    Iterates per ``Animal`` when the column is present, otherwise treats the
    whole group as a single series. Returns the list of finite cosinor parameter
    dicts and the list of finite dominant periods.
    """
    if "Animal" in group_df.columns:
        iterator = [g for _, g in group_df.groupby("Animal", observed=True)]
    else:
        iterator = [group_df]

    params: list[dict[str, float]] = []
    periods: list[float] = []
    for animal_df in iterator:
        t = _to_hours_since_start(animal_df["DateTime"], reference)
        y = animal_df[variable_name].to_numpy(dtype=float)
        fit = _fit_cosinor(t, y, period_hours)
        if np.isfinite(fit["MESOR"]):
            params.append(fit)
        _, _, dominant = _lombscargle_period(t, y)
        if np.isfinite(dominant):
            periods.append(dominant)
    return params, periods


def _per_animal_table(
    df: pd.DataFrame,
    variable_name: str,
    reference: pd.Timestamp,
    period_hours: float,
    zt_offset: float,
) -> pd.DataFrame:
    """One row per animal with its single-component cosinor and dominant-period fit.

    Unlike ``_per_animal_fits`` (which discards the animal id and aggregates to a group
    row), this keeps the ``Animal`` id so the result is a tidy, ANOVA-ready table: one
    observation per animal, with dataset factors attachable via ``set_factors``.
    """
    rows: list[dict] = []
    for animal, g in df.groupby("Animal", observed=True):
        t = _to_hours_since_start(g["DateTime"], reference)
        y = g[variable_name].to_numpy(dtype=float)
        fit = _fit_cosinor(t, y, period_hours)
        _, _, dominant = _lombscargle_period(t, y)
        rows.append({
            "Animal": str(animal),
            "MESOR": fit["MESOR"],
            "Amplitude": fit["Amplitude"],
            "Acrophase (ZT h)": (fit["Acrophase_h"] + zt_offset) % period_hours,
            "Dominant period (h)": dominant,
            "PR": fit["PR"],
            "p_value": fit["p_value"],
            "Rhythmic (p<0.05)": bool(fit["p_value"] < 0.05),
        })
    return pd.DataFrame(rows)


def _summarize_cosinor(
    label: str,
    params: list[dict[str, float]],
    period_hours: float,
    zt_offset: float,
) -> dict:
    """Aggregate per-animal cosinor parameters into a single group row."""
    n = len(params)
    if n == 0:
        return {
            "Group": label,
            "N animals": 0,
            "MESOR": float("nan"),
            "MESOR SEM": float("nan"),
            "Amplitude": float("nan"),
            "Amplitude SEM": float("nan"),
            "Acrophase (ZT h)": float("nan"),
            "Mean PR": float("nan"),
            "Rhythmic (p<0.05)": 0,
        }
    mesor = np.array([p["MESOR"] for p in params])
    amplitude = np.array([p["Amplitude"] for p in params])
    acrophase = np.array([p["Acrophase_h"] for p in params])
    pr = np.array([p["PR"] for p in params])
    pvals = np.array([p["p_value"] for p in params])
    acro_zt = _circular_mean_hours((acrophase + zt_offset) % period_hours, period_hours)
    return {
        "Group": label,
        "N animals": n,
        "MESOR": float(np.mean(mesor)),
        "MESOR SEM": _sem(mesor),
        "Amplitude": float(np.mean(amplitude)),
        "Amplitude SEM": _sem(amplitude),
        "Acrophase (ZT h)": acro_zt,
        "Mean PR": float(np.mean(pr)),
        "Rhythmic (p<0.05)": int(np.sum(pvals < 0.05)),
    }


def _summarize_periods(label: str, periods: list[float]) -> dict:
    """Aggregate per-animal dominant periods into a single group row."""
    if not periods:
        return {"Group": label, "N animals": 0, "Dominant period (h)": float("nan"), "SD (h)": float("nan")}
    arr = np.array(periods, dtype=float)
    return {
        "Group": label,
        "N animals": int(arr.size),
        "Dominant period (h)": float(np.mean(arr)),
        "SD (h)": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
    }


def _detect_onset_offset(
    df_animal: pd.DataFrame,
    variable_name: str,
    threshold_pct: float,
    light_cycle_start: time,
) -> pd.DataFrame:
    """Per-circadian-day onset/offset in Zeitgeber time.

    The day boundary is aligned to lights-on (ZT 0) by shifting timestamps by
    ``-light_cycle_start`` before grouping, so activity that spans midnight is
    not split across two calendar days. Onset/offset are the first/last samples
    crossing the per-day percentile threshold, reported as ZT hours.
    """
    df_animal = df_animal[["DateTime", variable_name]].dropna().copy()
    ls = pd.Timedelta(
        hours=light_cycle_start.hour,
        minutes=light_cycle_start.minute,
        seconds=light_cycle_start.second,
    )
    df_animal["CircDay"] = (df_animal["DateTime"] - ls).dt.date
    df_animal["ZT"] = _compute_zeitgeber_time(df_animal["DateTime"], light_cycle_start)
    rows: list[dict] = []
    for day, group in df_animal.groupby("CircDay", sort=True):
        if group[variable_name].nunique() < 2:
            continue
        threshold = float(np.nanpercentile(group[variable_name].to_numpy(), threshold_pct))
        above = group[group[variable_name] >= threshold].sort_values("DateTime")
        if above.empty:
            continue
        alpha = (above["DateTime"].iloc[-1] - above["DateTime"].iloc[0]).total_seconds() / 3600.0
        rows.append({
            "Day": str(day),
            "Onset (ZT)": float(above["ZT"].iloc[0]),
            "Offset (ZT)": float(above["ZT"].iloc[-1]),
            "Alpha_h": alpha,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Section plots
# ---------------------------------------------------------------------------


def _plot_zt_profile(
    df: pd.DataFrame,
    variable: Variable,
    light_cycle_start: time,
    dark_zt: float,
    group_col: str | None,
    palette: dict[str, str] | None,
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

    # Shade the dark phase using the configured light/dark cycle (ZT 0 = lights on).
    ax.axvspan(dark_zt, 24, color="gray", alpha=0.15, zorder=0)
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
    palette: dict[str, str] | None,
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
    zt_offset: float,
    palette: dict[str, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    omega = 2 * np.pi / period_hours
    for i, (label, (t, y, params)) in enumerate(fits.items()):
        if not np.isfinite(params.get("MESOR", np.nan)):
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        zt_phase = (t + zt_offset) % period_hours
        ax.scatter(zt_phase, y, alpha=0.25, s=8, color=color)
        zt_grid = np.linspace(0, period_hours, 200)
        y_fit = params["MESOR"] + params["Amplitude"] * np.cos(
            omega * (zt_grid - zt_offset) - omega * params["Acrophase_h"]
        )
        acro_zt = (params["Acrophase_h"] + zt_offset) % period_hours
        ax.plot(zt_grid, y_fit, color=color, label=f"{label} (A={params['Amplitude']:.2f}, φ={acro_zt:.1f} ZT)")
    ax.set_xlabel("Zeitgeber time (h)")
    ax.set_ylabel(f"{variable.name} ({variable.unit})" if variable.unit else variable.name)
    ax.set_title(f"Cosinor fits — {variable.name}")
    ax.set_xlim(0, period_hours)
    ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def _plot_two_component_fits(
    fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]],
    variable: Variable,
    period1_hours: float,
    period2_hours: float,
    zt_offset: float,
    palette: dict[str, str] | None,
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
        zt_phase = (t + zt_offset) % period1_hours
        ax.scatter(zt_phase, y, alpha=0.25, s=8, color=color)
        zt_grid = np.linspace(0, period1_hours, 400)
        t_grid = zt_grid - zt_offset
        y_fit = (
            params["MESOR"]
            + params["Amplitude_1"] * np.cos(omega1 * t_grid - omega1 * params["Acrophase_1_h"])
            + params["Amplitude_2"] * np.cos(omega2 * t_grid - omega2 * params["Acrophase_2_h"])
        )
        ax.plot(
            zt_grid,
            y_fit,
            color=color,
            label=f"{label} (A₁={params['Amplitude_1']:.2f}, A₂={params['Amplitude_2']:.2f})",
        )
    ax.set_xlabel("Zeitgeber time (h)")
    ax.set_ylabel(f"{variable.name} ({variable.unit})" if variable.unit else variable.name)
    ax.set_title(f"Two-component cosinor fits — {variable.name}")
    ax.set_xlim(0, period1_hours)
    ax.legend(fontsize="small")
    ax.grid(True, alpha=0.3)
    return figure


def _plot_onset_offset(
    onsets: dict[str, pd.DataFrame],
    palette: dict[str, str] | None,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()
    for i, (label, df) in enumerate(onsets.items()):
        if df.empty:
            continue
        color = (palette or {}).get(str(label), color_manager.get_color_hex(i))
        days = np.arange(1, len(df) + 1)
        ax.plot(df["Onset (ZT)"], days, marker="o", linestyle="-", color=color, label=f"{label} onset")
        ax.plot(df["Offset (ZT)"], days, marker="s", linestyle="--", color=color, label=f"{label} offset")
    ax.set_xlabel("Zeitgeber time (h)")
    ax.set_ylabel("Circadian day")
    ax.set_title("Activity onset / offset per circadian day")
    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(fontsize="small", ncol=2)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    return figure


def get_chronobiology_result(
    datatable: Datatable,
    variable: Variable,
    factor_name: str,
    period_hours: float = 24.0,
    period2_hours: float = 12.0,
    bins_per_hour: int = 6,
    onset_threshold_pct: float = 50.0,
    figsize: tuple[float, float] | None = None,
) -> ChronobiologyResult:
    dataset = datatable.dataset
    has_datetime = "DateTime" in datatable.df.columns

    # Always fetch Animal (so animal counts and per-animal cosinor are correct);
    # de-duplicate so a "group by Animal" request doesn't select the column twice.
    wanted = (["DateTime"] if has_datetime else []) + ["Animal", factor_name, variable.name]
    columns = list(dict.fromkeys(c for c in wanted if c in datatable.df.columns))
    df = datatable.get_filtered_df(columns).dropna()

    time_cycles = dataset.light_cycles
    light_cycle_start = time_cycles.light_cycle_start
    dark_cycle_start = time_cycles.dark_cycle_start

    sections: list[str] = []
    tables: dict[str, ResultTable] = {}
    # Result tables are only exposed for the "Add Datatable" feature when grouping by
    # Animal, so every table carries an "Animal" id column and is directly usable for
    # further per-animal analysis (e.g. ANOVA). Grouping by a factor yields per-group
    # aggregates (one row per group) that are not ANOVA-able, so nothing is offered.
    expose_tables = factor_name == "Animal"

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
            "Group by": factor_name,
        }
    ])
    sections.append(
        get_great_table(
            summary_df.T.reset_index().rename(columns={"index": "Field", 0: "Value"}), "Summary"
        ).as_raw_html(inline_css=True)
    )

    if not has_datetime:
        sections.append("<p><em>DateTime column not available — time-series sections skipped.</em></p>")
        return ChronobiologyResult(report="\n<p>\n".join(sections), tables=tables)

    # Common reference and group column resolution -------------------------
    reference_time = dataset.experiment_started
    zt_offset = _zeitgeber_offset(reference_time, light_cycle_start)
    dark_zt = (time_to_float(dark_cycle_start) - time_to_float(light_cycle_start)) % 24.0
    group_col = factor_name

    palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
    if not isinstance(palette, dict):
        palette = {}

    # Group-mean series (per factor level × DateTime) for visualisations.
    # The raw per-animal ``df`` is kept for the per-animal cosinor aggregation.
    if factor_name != "Animal":
        grouped_df = (
            df
            .copy()
            .groupby([factor_name, "DateTime"], dropna=False, observed=False)
            .aggregate({variable.name: "mean"})
            .reset_index()
        )
    else:
        grouped_df = df.copy()

    key_col = group_col

    # --- Section 2: ZT profile --------------------------------------------
    sections.append("<h3>Zeitgeber-time profile</h3>")
    sections.append(
        get_html_image_from_figure(
            _plot_zt_profile(grouped_df, variable, light_cycle_start, dark_zt, group_col, palette, figsize)
        )
    )

    # --- Per-group computation (single pass over group-mean series) -------
    ls_series: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}
    cosinor_fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]] = {}
    two_comp_fits: dict[str, tuple[np.ndarray, np.ndarray, dict[str, float]]] = {}
    two_comp_rows: list[dict] = []
    for label, g in grouped_df.groupby(key_col, observed=True):
        label = str(label)
        t = _to_hours_since_start(g["DateTime"], reference_time)
        y = g[variable.name].to_numpy(dtype=float)

        ls_series[label] = _lombscargle_period(t, y)
        cosinor_fits[label] = (t, y, _fit_cosinor(t, y, period_hours))

        tc_params = _fit_two_component_cosinor(t, y, period_hours, period2_hours)
        two_comp_fits[label] = (t, y, tc_params)
        two_comp_rows.append({
            "Group": label,
            "MESOR": tc_params["MESOR"],
            "Amplitude 1": tc_params["Amplitude_1"],
            "Acrophase 1 (ZT h)": (tc_params["Acrophase_1_h"] + zt_offset) % period_hours,
            "Amplitude 2": tc_params["Amplitude_2"],
            "Acrophase 2 (ZT h)": (tc_params["Acrophase_2_h"] + zt_offset) % period2_hours,
            "PR": tc_params["PR"],
            "p_value": tc_params["p_value"],
            "N": tc_params["N"],
        })

    # Per-animal aggregation (single-component cosinor + dominant period).
    cosinor_rows: list[dict] = []
    ls_table_rows: list[dict] = []
    for label, g in df.groupby(key_col, observed=True):
        label = str(label)
        animal_params, animal_periods = _per_animal_fits(g, variable.name, reference_time, period_hours)
        cosinor_rows.append(_summarize_cosinor(label, animal_params, period_hours, zt_offset))
        ls_table_rows.append(_summarize_periods(label, animal_periods))

    # Per-animal parameter table (one row per animal) — the ANOVA-ready result.
    if expose_tables and "Animal" in df.columns:
        per_animal_df = _per_animal_table(df, variable.name, reference_time, period_hours, zt_offset)
        if not per_animal_df.empty:
            tables["Per-animal parameters"] = ResultTable(per_animal_df, "Animal")

    # --- Section 3: Lomb–Scargle periodogram ------------------------------
    sections.append("<h3>Lomb–Scargle periodogram</h3>")
    sections.append(get_html_image_from_figure(_plot_periodogram(ls_series, variable, palette, figsize)))
    ls_table_df = pd.DataFrame(ls_table_rows)
    sections.append(get_great_table(ls_table_df, "Dominant periods (per-animal mean)").as_raw_html(inline_css=True))
    if expose_tables:
        tables["Dominant periods"] = ResultTable(ls_table_df.rename(columns={"Group": factor_name}), factor_name)

    # --- Section 4: single-component cosinor ------------------------------
    sections.append(f"<h3>Single-component cosinor (period = {period_hours:g} h)</h3>")
    cosinor_df = pd.DataFrame(cosinor_rows)
    sections.append(
        get_great_table(cosinor_df, "Cosinor parameters (per-animal mean ± SEM)").as_raw_html(inline_css=True)
    )
    if expose_tables:
        tables["Cosinor parameters"] = ResultTable(cosinor_df.rename(columns={"Group": factor_name}), factor_name)
    sections.append(
        "<p><em>p-values assume independent residuals and are anti-conservative for autocorrelated "
        "series; the between-animal aggregation (N animals, SEM, rhythmic count) is the more reliable "
        "indicator. Curves show the cosinor fit on the group-mean series.</em></p>"
    )
    sections.append(
        get_html_image_from_figure(
            _plot_cosinor_fits(cosinor_fits, variable, period_hours, zt_offset, palette, figsize)
        )
    )

    # --- Section 4b: two-component cosinor --------------------------------
    sections.append(f"<h3>Two-component cosinor (periods = {period_hours:g} h + {period2_hours:g} h)</h3>")
    two_comp_df = pd.DataFrame(two_comp_rows)
    sections.append(
        get_great_table(two_comp_df, "Two-component cosinor parameters (group-mean series)").as_raw_html(
            inline_css=True
        )
    )
    if expose_tables:
        tables["Two-component cosinor"] = ResultTable(two_comp_df.rename(columns={"Group": factor_name}), factor_name)
    sections.append(
        get_html_image_from_figure(
            _plot_two_component_fits(two_comp_fits, variable, period_hours, period2_hours, zt_offset, palette, figsize)
        )
    )

    # --- Section 5: activity onset / offset -------------------------------
    onset_tables: dict[str, pd.DataFrame] = {}
    onset_combined_rows: list[dict] = []
    for label, g in grouped_df.groupby(key_col, observed=True):
        label = str(label)
        table = _detect_onset_offset(g, variable.name, onset_threshold_pct, light_cycle_start)
        if not table.empty:
            onset_tables[label] = table
            for _, row in table.iterrows():
                onset_combined_rows.append({key_col: label, **row.to_dict()})

    sections.append(f"<h3>Activity onset / offset (threshold = {onset_threshold_pct:g}th percentile)</h3>")
    if onset_combined_rows:
        onset_df = pd.DataFrame(onset_combined_rows)
        sections.append(get_great_table(onset_df, "Daily onset / offset (ZT)").as_raw_html(inline_css=True))
        if expose_tables:
            tables["Activity onset / offset"] = ResultTable(onset_df, key_col)
        sections.append(get_html_image_from_figure(_plot_onset_offset(onset_tables, palette, figsize)))
    else:
        sections.append("<p><em>Not enough data to detect daily onset / offset.</em></p>")

    # --- Section 6: double-plotted actogram -------------------------------
    sections.append("<h3>Double-plotted actogram</h3>")
    if duration is None or duration < pd.Timedelta(hours=48):
        sections.append("<p><em>Experiment shorter than 48 h — actogram skipped.</em></p>")
    else:
        periods = _build_actogram_periods(light_cycle_start, dark_cycle_start)
        bins_per_day = 24 * bins_per_hour
        groups_data, shared_days = _collect_group_actograms(grouped_df, key_col, variable, bins_per_day)
        if len(groups_data) == 1:
            label, activity_array = next(iter(groups_data.items()))
            figure, _ = plot_enhanced_actogram(
                activity_array,
                figsize,
                [d.strftime("%Y-%m-%d") for d in shared_days],
                binsize=1 / bins_per_hour,
                highlight_periods=periods,
                bar_color=palette.get(label, color_manager.get_color_hex(0)),
                title=f"Actogram — {variable.name} ({label})",
            )
            sections.append(get_html_image_from_figure(figure))
        elif len(groups_data) >= 2:
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
    return ChronobiologyResult(report=report, tables=tables)
