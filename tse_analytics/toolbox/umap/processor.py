from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from matplotlib import rcParams
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class UmapResult:
    report: str


def get_umap_result(
    datatable: Datatable,
    variables: list[str],
    factor_name: str,
    n_neighbors: int,
    n_components: int,
    metric: str,
    min_dist: float,
    figsize: tuple[float, float] | None = None,
) -> UmapResult:
    # Lazy module import
    from umap import UMAP

    columns = [factor_name] + variables
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[variables])

    umap = UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric=metric,
        min_dist=min_dist,
    )
    data = umap.fit_transform(scaled_data)

    if figsize is None:
        figsize = rcParams["figure.figsize"]

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    match n_components:
        case 1:
            title = "UMAP (1D)"

            result_df = pd.DataFrame(data=data, columns=["UMAP1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="UMAP1",
                    y="N",
                    color=factor_name,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 2:
            title = "UMAP (2D)"

            result_df = pd.DataFrame({
                "UMAP1": data[:, 0],
                "UMAP2": data[:, 1],
            })
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="UMAP1",
                    y="UMAP2",
                    color=factor_name,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 3:
            title = "UMAP (3D)"

            result_df = pd.DataFrame({
                "UMAP1": data[:, 0],
                "UMAP2": data[:, 1],
                "UMAP3": data[:, 2],
            })
            result_df[factor_name] = df[factor_name].values

            figure, ax = plt.subplots(
                1,
                1,
                figsize=(figsize[0], figsize[0]),
                layout="tight",
                subplot_kw={"projection": "3d"},
            )

            for group, c in palette.items():
                group_df = result_df[result_df[factor_name] == group]
                ax.scatter(
                    group_df["UMAP1"],
                    group_df["UMAP2"],
                    group_df["UMAP3"],
                    c=c,
                    label=group,
                )
            ax.legend(title=factor_name)

            ax.set(
                xlabel="UMAP1",
                ylabel="UMAP2",
                zlabel="UMAP3",
                title=title,
            )

    report = get_html_image_from_figure(figure)

    return UmapResult(
        report=report,
    )
