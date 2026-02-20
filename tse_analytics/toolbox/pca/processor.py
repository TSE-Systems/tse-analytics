from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.toolbox.pca.plots import pca_explained_variance_plot, variable_contributions_plot


@dataclass
class PcaResult:
    report: str


def get_pca_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> PcaResult:
    match split_mode:
        case SplitMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            by = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            by = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
        case _:
            by = None
            palette = color_manager.colormap_name

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[variables])

    pca = PCA()
    data = pca.fit_transform(scaled_data)

    explained_variance_figure = pca_explained_variance_plot(pca, figsize)
    variable_contributions_figure = variable_contributions_plot(pca, variables, (figsize[0], figsize[1] / 2))

    if by is not None:
        result_df = pd.DataFrame({
            "Principal component 1": data[:, 0],
            "Principal component 2": data[:, 1],
            "Principal component 3": data[:, 2],
            by: df[by],
        })
    else:
        result_df = pd.DataFrame({
            "Principal component 1": data[:, 0],
            "Principal component 2": data[:, 1],
            "Principal component 3": data[:, 2],
        })

    # Create a figure with a tight layout
    figure_2d_scores = plt.Figure(figsize=figsize, layout="tight")
    (
        so
        .Plot(
            result_df,
            x="Principal component 1",
            y="Principal component 2",
            color=by,
        )
        .add(so.Dot(pointsize=3))
        .scale(color=palette)
        .label(title="PCA Scores (2D)")
        .on(figure_2d_scores)
        .plot(True)
    )

    figure_3d_scores, ax = plt.subplots(
        1,
        1,
        figsize=(figsize[0], figsize[0]),
        layout="tight",
        subplot_kw={"projection": "3d"},
    )

    if by is not None:
        for group, c in palette.items():
            mask = df[by] == group
            ax.scatter(
                result_df.loc[mask, "Principal component 1"],
                result_df.loc[mask, "Principal component 2"],
                result_df.loc[mask, "Principal component 3"],
                c=c,
                label=group,
            )
        ax.legend(title=by)
    else:
        ax.scatter(
            data=result_df,
            xs="Principal component 1",
            ys="Principal component 2",
            zs="Principal component 3",
        )

    ax.set(
        xlabel="Principal component 1",
        ylabel="Principal component 2",
        zlabel="Principal component 3",
        title="PCA Scores (3D)",
    )

    report = f"""
    {get_html_image_from_figure(explained_variance_figure)}
    <p>
    {get_html_image_from_figure(variable_contributions_figure)}
    <p>
    {get_html_image_from_figure(figure_2d_scores)}
    <p>
    {get_html_image_from_figure(figure_3d_scores)}
    """

    return PcaResult(
        report=report,
    )
