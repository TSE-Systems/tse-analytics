from dataclasses import dataclass

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import rcParams

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure


@dataclass
class CorrelationMatrixResult:
    report: str


def get_correlation_matrix_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    figsize: tuple[float, float] | None = None,
) -> CorrelationMatrixResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

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
