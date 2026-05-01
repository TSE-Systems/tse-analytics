from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from matplotlib import rcParams
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings
from tse_analytics.toolbox.pca.plots import pca_explained_variance_plot, variable_contributions_plot


@dataclass
class PcaResult:
    report: str


def get_pca_result(
    datatable: Datatable,
    variables: list[str],
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> PcaResult:
    columns = get_columns_by_grouping_settings(grouping_settings, variables)
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[by])

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[variables])

    pca = PCA()
    data = pca.fit_transform(scaled_data)

    if figsize is None:
        figsize = rcParams["figure.figsize"]

    explained_variance_figure = pca_explained_variance_plot(pca, figsize)
    variable_contributions_figure = variable_contributions_plot(pca, variables, (figsize[0], figsize[1] / 2))

    result_df = pd.DataFrame({
        "Principal component 1": data[:, 0],
        "Principal component 2": data[:, 1],
        "Principal component 3": data[:, 2],
    })
    if by is not None:
        result_df[by] = df[by].values

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
