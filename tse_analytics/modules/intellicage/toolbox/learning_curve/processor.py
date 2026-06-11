"""Processing for the IntelliCage Learning Curve toolbox widget.

Computes a per-animal performance metric across consecutive learning bins
(either time intervals or visit blocks) and renders the resulting learning
curves plus a per-animal summary table as an HTML report.
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure

# Metric identifiers (kept in sync with the widget's combo box).
METRIC_CORRECT_VISITS = "% Correct visits"
METRIC_PLACE_ERROR_RATE = "Place-error rate"
METRIC_NOSEPOKE_ERROR_RATE = "Nosepoke error rate"
METRIC_LICKS_PER_VISIT = "Licks per visit"

# Binning modes (kept in sync with the widget's combo box).
BIN_MODE_TIME = "Time interval"
BIN_MODE_VISIT = "Visit block"

# Visits columns each metric needs; used by the widget to validate the datatable.
METRIC_REQUIRED_COLUMNS: dict[str, list[str]] = {
    METRIC_CORRECT_VISITS: ["CornerCondition"],
    METRIC_PLACE_ERROR_RATE: ["PlaceError"],
    METRIC_NOSEPOKE_ERROR_RATE: ["SideErrors", "NosepokesNumber"],
    METRIC_LICKS_PER_VISIT: ["LicksNumber"],
}

# Y-axis label per metric.
_METRIC_AXIS_LABEL: dict[str, str] = {
    METRIC_CORRECT_VISITS: "Correct visits (%)",
    METRIC_PLACE_ERROR_RATE: "Place-error rate",
    METRIC_NOSEPOKE_ERROR_RATE: "Nosepoke error rate",
    METRIC_LICKS_PER_VISIT: "Licks per visit",
}


@dataclass
class IntelliCageLearningCurveResult:
    report: str
    curve_data: pd.DataFrame
    summary: pd.DataFrame


def get_intellicage_learning_curve_result(
    dataset: Dataset,
    df: pd.DataFrame,
    metric: str,
    bin_mode: str,
    bin_size: int,
    group_by: str,
    figsize: tuple[float, float] | None = None,
) -> IntelliCageLearningCurveResult:
    """Compute learning curves and a summary table for an IntelliCage Visits dataframe.

    Args:
        dataset: Owning dataset (used for group colour palettes).
        df: Filtered Visits dataframe containing at least ``Animal``, ``Timedelta``,
            the metric's required column(s), and the ``group_by`` column.
        metric: One of the ``METRIC_*`` identifiers.
        bin_mode: One of the ``BIN_MODE_*`` identifiers.
        bin_size: Bin width — hours for time intervals, visit count for visit blocks.
        group_by: Factor name used to colour/aggregate the curves (e.g. ``"Animal"``).
        figsize: Optional figure size in inches.

    Returns:
        The rendered report plus the long-form per-(animal, bin) metric table and the
        per-animal learning summary.
    """
    df = df.copy()
    df = _assign_bins(df, bin_mode, bin_size)

    group_keys = ["Animal", "Bin"] if group_by == "Animal" else [group_by, "Animal", "Bin"]
    curve_data = _compute_metric(df, metric, group_keys)

    figure = _plot_curves(curve_data, dataset, metric, bin_mode, bin_size, group_by, figsize)
    summary = _build_summary(curve_data, group_by)

    html_template = """
                    {curve}
                    {summary}
                    """
    report = html_template.format(
        curve=get_html_image_from_figure(figure),
        summary=get_great_table(summary, "Learning Summary").as_raw_html(inline_css=True),
    )

    return IntelliCageLearningCurveResult(
        report=report,
        curve_data=curve_data,
        summary=summary,
    )


def _assign_bins(df: pd.DataFrame, bin_mode: str, bin_size: int) -> pd.DataFrame:
    """Add an integer ``Bin`` column describing learning progress."""
    df = df.sort_values(["Animal", "Timedelta"])
    if bin_mode == BIN_MODE_VISIT:
        df["Bin"] = df.groupby("Animal", observed=True).cumcount() // bin_size
    else:
        interval = pd.Timedelta(hours=bin_size)
        df["Bin"] = df["Timedelta"] // interval
    df["Bin"] = df["Bin"].astype("int64")
    return df


def _compute_metric(df: pd.DataFrame, metric: str, group_keys: list[str]) -> pd.DataFrame:
    """Reduce the per-visit rows to one metric value per group/animal/bin."""
    if metric == METRIC_CORRECT_VISITS:
        df = df.assign(_value=df["CornerCondition"].eq("Correct").astype("float64"))
        value = df.groupby(group_keys, observed=True)["_value"].mean() * 100.0
    elif metric == METRIC_PLACE_ERROR_RATE:
        value = df.groupby(group_keys, observed=True)["PlaceError"].mean()
    elif metric == METRIC_NOSEPOKE_ERROR_RATE:
        agg = df.groupby(group_keys, observed=True).agg(
            _side=("SideErrors", "sum"),
            _pokes=("NosepokesNumber", "sum"),
        )
        value = (agg["_side"] / agg["_pokes"]).where(agg["_pokes"] > 0)
    elif metric == METRIC_LICKS_PER_VISIT:
        value = df.groupby(group_keys, observed=True)["LicksNumber"].mean()
    else:
        raise ValueError(f"Unknown metric: {metric!r}")

    curve_data = value.reset_index(name="Metric").dropna(subset=["Metric"])
    curve_data["Metric"] = curve_data["Metric"].astype("float64")
    return curve_data


def _plot_curves(
    curve_data: pd.DataFrame,
    dataset: Dataset,
    metric: str,
    bin_mode: str,
    bin_size: int,
    group_by: str,
    figsize: tuple[float, float] | None,
) -> plt.Figure:
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots(1, 1)

    palette = color_manager.get_level_to_color_dict(dataset.factors[group_by])
    palette = palette if isinstance(palette, dict) else None

    if group_by == "Animal":
        # Each animal is its own learning curve.
        sns.lineplot(
            data=curve_data,
            x="Bin",
            y="Metric",
            hue="Animal",
            marker="o",
            palette=palette,
            ax=ax,
        )
    else:
        # One line per factor level: group mean ± SEM band (no individual animals).
        sns.lineplot(
            data=curve_data,
            x="Bin",
            y="Metric",
            hue=group_by,
            estimator="mean",
            errorbar="se",
            marker="o",
            palette=palette,
            ax=ax,
        )

    xlabel = f"Visit block (×{bin_size} visits)" if bin_mode == BIN_MODE_VISIT else f"Time bin (×{bin_size} h)"
    ax.set(
        xlabel=xlabel,
        ylabel=_METRIC_AXIS_LABEL[metric],
        title=f"Learning curve: {metric}",
    )
    return figure


def _build_summary(curve_data: pd.DataFrame, group_by: str) -> pd.DataFrame:
    """Per-animal start/end performance, change, and linear learning slope."""
    keys = ["Animal"] if group_by == "Animal" else [group_by, "Animal"]
    rows = []
    for key_vals, group in curve_data.groupby(keys, observed=True):
        # groupby yields a scalar key for a single grouper and a tuple for several;
        # normalize to a tuple so indexing below is uniform across pandas versions.
        if not isinstance(key_vals, tuple):
            key_vals = (key_vals,)

        group = group.sort_values("Bin")
        if len(group) >= 2:
            slope = float(linregress(group["Bin"].to_numpy(float), group["Metric"].to_numpy(float)).slope)
        else:
            slope = float("nan")

        start = float(group["Metric"].iloc[0])
        end = float(group["Metric"].iloc[-1])

        row: dict[str, object] = {}
        if group_by == "Animal":
            row["Animal"] = key_vals[0]
        else:
            row[group_by] = key_vals[0]
            row["Animal"] = key_vals[1]
        row["Start"] = start
        row["End"] = end
        row["Change"] = end - start
        row["Slope"] = slope
        row["Bins"] = len(group)
        rows.append(row)

    return pd.DataFrame(rows)
