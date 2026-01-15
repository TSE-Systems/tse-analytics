from dataclasses import dataclass

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import chi2

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class IntelliCageTransitionsResult:
    report: str


def get_intellicage_transitions_result(
    dataset: Dataset,
    df: pd.DataFrame,
    animal_ids: list[str],
    alpha: float = 0.05,
    figsize: tuple[float, float] | None = None,
) -> IntelliCageTransitionsResult:
    report = "<h1>Chi-Square Analysis of Corner Transitions</h1><br>"
    for animal_id in animal_ids:
        animal_report = _process_animal(
            df,
            animal_id,
            alpha,
            figsize,
        )
        if animal_report is not None:
            report += animal_report + "<br>"

    return IntelliCageTransitionsResult(
        report=report,
    )


def _process_animal(
    df: pd.DataFrame,
    animal_id: str,
    alpha: float,
    figsize: tuple[float, float],
) -> str | None:
    animal_df = df[df["Animal"] == animal_id].copy()
    if animal_df.empty:
        return None

    animal_df.reset_index(drop=True, inplace=True)

    # Sort by timestamp to get the sequence of visits
    animal_df.sort_values("Timedelta", inplace=True)

    # Create pairs of consecutive corners to analyze transitions
    animal_df["NextCorner"] = animal_df["Corner"].shift(-1)

    # Remove the last row as it doesn't have a next corner
    animal_df = animal_df.dropna(subset=["NextCorner"])

    # Convert corner numbers to integers if they aren't already
    animal_df["NextCorner"] = animal_df["NextCorner"].astype(int)

    # Create a transition matrix
    observed_matrix = pd.crosstab(animal_df["Corner"], animal_df["NextCorner"])

    # Calculate expected transition matrix
    # Expected counts = (row sum * column sum) / total
    row_sums = observed_matrix.sum(axis=1)
    col_sums = observed_matrix.sum(axis=0)
    total = observed_matrix.values.sum()

    expected = np.outer(row_sums, col_sums) / total
    expected_matrix = pd.DataFrame(expected, index=observed_matrix.index, columns=observed_matrix.columns)

    # Chi-square test for each cell
    chi_square = (observed_matrix - expected_matrix) ** 2 / expected_matrix

    # Calculate p-values
    p_values = pd.DataFrame(
        chi2.sf(chi_square.values, df=1),  # df=1 for each cell
        index=observed_matrix.index,
        columns=observed_matrix.columns,
    )

    # Highlight significant transitions
    # Create a mask for significant transitions (p < alpha)
    significant = p_values < alpha

    # Create a ratio matrix (observed/expected)
    ratio = observed_matrix / expected
    # Replace inf values with NaN
    ratio = ratio.replace([np.inf, -np.inf], np.nan)

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

    return get_html_image_from_figure(figure)
