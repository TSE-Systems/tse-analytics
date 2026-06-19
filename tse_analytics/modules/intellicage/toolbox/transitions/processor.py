from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2

from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class IntelliCageTransitionsResult:
    report: str
    # Per-animal transition matrices, keyed by animal id then matrix name
    # ("Observed", "Expected", "Chi-Square", "P-Values", "Ratio").
    matrices: dict[str, dict[str, pd.DataFrame]] = field(default_factory=dict)


def get_intellicage_transitions_result(
    df: pd.DataFrame,
    alpha: float = 0.05,
    include_diagonal: bool = True,
    figsize: tuple[float, float] | None = None,
) -> IntelliCageTransitionsResult:
    report = "<h1>Chi-Square Analysis of Corner Transitions</h1><br>"
    matrices: dict[str, dict[str, pd.DataFrame]] = {}

    for animal_id in sorted(df["Animal"].dropna().unique()):
        result = _process_animal(
            df,
            animal_id,
            alpha,
            include_diagonal,
            figsize,
        )
        if result is not None:
            animal_report, animal_matrices = result
            report += animal_report + "<br>"
            matrices[str(animal_id)] = animal_matrices

    return IntelliCageTransitionsResult(
        report=report,
        matrices=matrices,
    )


def _process_animal(
    df: pd.DataFrame,
    animal_id: str,
    alpha: float,
    include_diagonal: bool,
    figsize: tuple[float, float] | None,
) -> tuple[str, dict[str, pd.DataFrame]] | None:
    animal_df = df[df["Animal"] == animal_id].copy()
    if animal_df.empty:
        return None

    # Sort by timestamp to get the sequence of visits
    animal_df.sort_values("Timedelta", inplace=True)

    # Create pairs of consecutive corners to analyze transitions
    animal_df["NextCorner"] = animal_df["Corner"].shift(-1)

    # Remove the last row as it doesn't have a next corner
    animal_df = animal_df.dropna(subset=["NextCorner"])

    # Optionally drop self-transitions (consecutive visits to the same corner)
    if not include_diagonal:
        animal_df = animal_df[animal_df["Corner"] != animal_df["NextCorner"]]

    if animal_df.empty:
        return None

    # Convert corner numbers to integers if they aren't already
    animal_df["NextCorner"] = animal_df["NextCorner"].astype("UInt8")

    # Create a transition matrix
    observed_matrix = pd.crosstab(animal_df["Corner"], animal_df["NextCorner"])
    if observed_matrix.empty:
        return None

    # Square the matrix so "From" and "To" axes share the same corner labels,
    # making the diagonal and the heatmaps directly comparable.
    corners = sorted(set(observed_matrix.index) | set(observed_matrix.columns))
    observed_matrix = observed_matrix.reindex(index=corners, columns=corners, fill_value=0)

    total = observed_matrix.values.sum()
    if total == 0:
        return None

    # Calculate expected transition matrix
    # Expected counts = (row sum * column sum) / total
    row_sums = observed_matrix.sum(axis=1)
    col_sums = observed_matrix.sum(axis=0)

    expected = np.outer(row_sums, col_sums) / total
    expected_matrix = pd.DataFrame(expected, index=observed_matrix.index, columns=observed_matrix.columns)

    # Corners that are only ever a source (or only ever a destination) have a zero
    # margin and therefore a zero expected count; mask those cells so they render
    # blank instead of producing inf/0-division artifacts.
    zero_expected = expected_matrix == 0

    # Chi-square test for each cell
    with np.errstate(divide="ignore", invalid="ignore"):
        chi_square = (observed_matrix - expected_matrix) ** 2 / expected_matrix
        ratio = observed_matrix / expected_matrix
    chi_square = chi_square.mask(zero_expected)
    ratio = ratio.replace([np.inf, -np.inf], np.nan).mask(zero_expected)

    # Calculate p-values (df=1 for each cell)
    p_values = pd.DataFrame(
        chi2.sf(chi_square.values, df=1),
        index=observed_matrix.index,
        columns=observed_matrix.columns,
    ).mask(zero_expected)

    # Highlight significant transitions (p < alpha); NaN cells are treated as not significant.
    significant = p_values < alpha

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")
    axs = figure.subplots(2, 2)

    sns.heatmap(
        observed_matrix,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidth=0.5,
        ax=axs[0, 0],
    )
    axs[0, 0].set(
        xlabel="To Corner",
        ylabel="From Corner",
        title="Observed transitions",
    )

    sns.heatmap(
        expected_matrix,
        annot=True,
        fmt=".1f",
        cmap="YlGnBu",
        linewidth=0.5,
        ax=axs[0, 1],
    )
    axs[0, 1].set(
        xlabel="To Corner",
        ylabel="From Corner",
        title="Expected transitions",
    )

    sns.heatmap(
        chi_square,
        annot=True,
        fmt=".2f",
        cmap="Reds",
        linewidth=0.5,
        ax=axs[1, 0],
    )
    axs[1, 0].set(
        xlabel="To Corner",
        ylabel="From Corner",
        title="Chi-Square Values",
    )

    # Plot the ratio with asterisks for significant transitions
    sns.heatmap(
        ratio,
        annot=significant.map(lambda x: "**" if x else ""),
        fmt="",
        cmap="RdBu_r",
        linewidth=0.5,
        center=1.0,
        ax=axs[1, 1],
    )
    axs[1, 1].set(
        xlabel="To Corner",
        ylabel="From Corner",
        title=f"Observed/Expected Ratio (** = p < {alpha})",
    )

    figure.suptitle(f"Animal: {animal_id}")

    animal_matrices = {
        "Observed": observed_matrix,
        "Expected": expected_matrix,
        "Chi-Square": chi_square,
        "P-Values": p_values,
        "Ratio": ratio,
    }

    return get_html_image_from_figure(figure), animal_matrices
