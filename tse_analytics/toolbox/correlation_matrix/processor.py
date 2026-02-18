from dataclasses import dataclass

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import rcParams, pyplot as plt

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure, get_great_table


@dataclass
class CorrelationMatrixResult:
    report: str


def get_correlation_matrix_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> CorrelationMatrixResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    match split_mode:
        case SplitMode.ANIMAL:
            hue = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            hue = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            hue = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
        case _:  # Total
            hue = "None"
            palette = color_manager.colormap_name

    # Compute the correlation matrix
    correlation_df = df[variables].corr()

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(correlation_df, dtype=bool))

    # Set up the matplotlib figure
    figure, ax = plt.subplots(figsize=(figsize[0] / 2, figsize[0] / 2))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(
        correlation_df,
        mask=mask,
        cmap=cmap,
        vmax=0.3,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
        ax=ax,
    ).set_title("Correlation plot")

    report = f"""
    {get_great_table(correlation_df.reset_index(), "Correlation matrix", rowname_col="index").as_raw_html(inline_css=True)}
    {get_html_image_from_figure(figure)}
    """

    return CorrelationMatrixResult(
        report=report,
    )
