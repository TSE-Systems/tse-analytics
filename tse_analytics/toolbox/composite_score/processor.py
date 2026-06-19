"""Composite performance score computation.

Collapses several per-animal numeric readouts into a single performance index
using the behavioral *z-score methodology* (Guilloux et al. 2011): aggregate per
animal, normalize each variable across animals, flip the sign of variables where
*lower is better*, weight, and average.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure


@dataclass
class CompositeScoreResult:
    report: str
    scores_df: pd.DataFrame


def compute_composite_scores(
    agg_df: pd.DataFrame,
    variables: list[str],
    directions: dict[str, str],
    weights: dict[str, float],
    normalization: str,
) -> tuple[pd.DataFrame, list[str]]:
    """Compute the per-animal composite score from already-aggregated data.

    Pure function (no Qt/plotting) so it can be unit-tested directly.

    Args:
        agg_df: One row per animal with an ``Animal`` column and one column per
            entry in ``variables`` (already aggregated).
        variables: Variable names to combine.
        directions: name -> ``"higher"`` | ``"lower"``.
        weights: name -> weight (>= 0).
        normalization: ``"zscore"`` or ``"minmax"``.

    Returns:
        A tuple ``(scores_df, warnings)``.  ``scores_df`` has ``Animal``, one
        signed-normalized column per variable, and a ``Score`` column.
        ``warnings`` holds human-readable notes about degenerate variables.
    """
    warnings: list[str] = []
    result = pd.DataFrame({"Animal": agg_df["Animal"].to_numpy()})

    normalized: dict[str, np.ndarray] = {}
    for name in variables:
        col = pd.to_numeric(agg_df[name], errors="coerce").to_numpy(dtype="float64")

        if normalization == "minmax":
            low = np.nanmin(col)
            high = np.nanmax(col)
            spread = high - low
            if not np.isfinite(spread) or spread == 0:
                z = np.zeros_like(col)
                warnings.append(f"Variable '{name}' has zero variance and was set to 0.")
            else:
                z = (col - low) / spread
        else:  # zscore
            mean = np.nanmean(col)
            std = np.nanstd(col, ddof=1)
            if not np.isfinite(std) or std == 0:
                z = np.zeros_like(col)
                warnings.append(f"Variable '{name}' has zero variance and was set to 0.")
            else:
                z = (col - mean) / std

        # Preserve missing values so they are skipped in the weighted mean.
        z = np.where(np.isnan(col), np.nan, z)

        if directions.get(name) == "lower":
            z = -z

        normalized[name] = z
        result[name] = z

    # Masked weighted mean across variables (per-animal NaNs are skipped).
    z_matrix = np.column_stack([normalized[name] for name in variables])
    weight_row = np.array([float(weights.get(name, 1.0)) for name in variables])
    present = ~np.isnan(z_matrix)
    numerator = np.nansum(np.where(present, z_matrix, 0.0) * weight_row, axis=1)
    denominator = (present * weight_row).sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        score = np.where(denominator > 0, numerator / denominator, np.nan)
    result["Score"] = score

    if weight_row.sum() == 0:
        warnings.append("All weights are zero; scores are undefined.")

    return result, warnings


def get_composite_score_result(
    datatable: Datatable,
    variables: list[str],
    directions: dict[str, str],
    weights: dict[str, float],
    normalization: str = "zscore",
    factor_name: str = "Animal",
    figsize: tuple[float, float] | None = None,
) -> CompositeScoreResult | None:
    """Build the composite-score report for the given datatable and settings.

    The score is always computed across all animals; ``factor_name`` only selects the
    factor whose colors tint the chart bars. ``"Animal"`` colors each bar by that
    animal's own color, any other factor colors each bar by the animal's group level.

    Returns ``None`` if fewer than two variables hold usable (non-empty) data.
    """
    # Resolve which factor (if any) tints the bars. "Animal" needs no extra column
    # (the bar's animal id is its level); any other factor needs a materialized column.
    color_by = factor_name if factor_name in datatable.dataset.factors else None
    level_column = color_by if color_by not in (None, "Animal") and color_by in datatable.df.columns else None
    if color_by not in (None, "Animal") and level_column is None:
        color_by = None  # selected factor isn't materialized -> fall back to a single color

    columns = ["Animal", *variables]
    if level_column is not None:
        columns.append(level_column)
    df = datatable.get_filtered_df(columns)

    # Aggregate each variable per animal using its own aggregation method.
    agg = (
        df
        .groupby("Animal", observed=True)
        .aggregate({name: datatable.variables[name].aggregation for name in variables})
        .reset_index()
    )

    warnings: list[str] = []

    # Drop variables that carry no data at all for the enabled animals.
    kept = []
    for name in variables:
        if agg[name].isna().all():
            warnings.append(f"Variable '{name}' has no data and was excluded.")
        else:
            kept.append(name)
    if len(kept) < 2:
        return None

    # The score is always computed across all animals; the "Color by" factor is used
    # purely to color the chart bars.
    scores, score_warnings = compute_composite_scores(agg, kept, directions, weights, normalization)
    warnings.extend(score_warnings)

    if agg["Animal"].nunique() < 2:
        warnings.append("Composite scoring needs at least two animals to be meaningful.")

    if level_column is not None:
        level_per_animal = df.groupby("Animal", observed=True)[level_column].first()
        scores[level_column] = scores["Animal"].map(level_per_animal).to_numpy()

    scores = scores.sort_values("Score", ascending=False, na_position="last").reset_index(drop=True)
    scores.insert(0, "Rank", range(1, len(scores) + 1))

    report = _build_report(
        datatable,
        scores,
        kept,
        normalization,
        color_by,
        warnings,
        figsize,
    )

    return CompositeScoreResult(report=report, scores_df=scores)


def _build_report(
    datatable: Datatable,
    scores: pd.DataFrame,
    variables: list[str],
    normalization: str,
    color_by: str | None,
    warnings: list[str],
    figsize: tuple[float, float] | None,
) -> str:
    normalization_label = "Min-max [0, 1]" if normalization == "minmax" else "Z-score (standardized)"

    display_columns = ["Rank", "Animal"]
    # "Animal" is already shown; only add a separate column for a different factor.
    if color_by is not None and color_by != "Animal":
        display_columns.append(color_by)
    display_columns += ["Score", *variables]
    display_df = scores[display_columns]

    table_html = get_great_table(
        display_df,
        "Composite performance score (per animal)",
        subtitle=f"Normalization: {normalization_label}. Variable columns show signed, normalized contributions.",
        rowname_col="Animal",
    ).as_raw_html(inline_css=True)

    chart_html = get_html_image_from_figure(_build_chart(datatable, scores, color_by, figsize))

    warnings_html = ""
    if warnings:
        items = "".join(f"<li>{message}</li>" for message in warnings)
        warnings_html = f"<p><b>Notes:</b></p><ul>{items}</ul>"

    return f"""
    {warnings_html}
    {table_html}
    {chart_html}
    """


def _build_chart(
    datatable: Datatable,
    scores: pd.DataFrame,
    color_by: str | None,
    figsize: tuple[float, float] | None,
):
    figure = plt.Figure(figsize=figsize, layout="tight")
    ax = figure.subplots()

    animals = scores["Animal"].astype(str).to_list()
    values = scores["Score"].to_numpy(dtype="float64")

    # Color bars by the selected factor's colors. For "Animal" the per-bar level is the
    # animal id itself; for any other factor it is the animal's attached group level.
    if color_by is not None:
        palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[color_by])
        if isinstance(palette, dict):
            levels = scores["Animal"] if color_by == "Animal" else scores[color_by]
            colors = [palette.get(str(level), "#808080") for level in levels]
        else:
            colors = palette
    else:
        colors = color_manager.get_factor_level_color_hex(0)

    ax.bar(animals, values, color=colors)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("Animal")
    ax.set_ylabel("Composite score")
    ax.set_title("Per-animal composite performance score")
    ax.tick_params(axis="x", labelrotation=90)

    return figure
