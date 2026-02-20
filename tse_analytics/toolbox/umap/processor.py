from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class UmapResult:
    report: str


def get_umap_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    split_mode: SplitMode,
    factor_name: str | None,
    n_neighbors: int,
    n_components: int,
    metric: str,
    min_dist: float,
    figsize: tuple[float, float] | None = None,
) -> UmapResult:
    # Lazy module import
    from umap import UMAP

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

    umap = UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric=metric,
        min_dist=min_dist,
    )
    data = umap.fit_transform(scaled_data)

    match n_components:
        case 1:
            title = "UMAP (1D)"
            result_df = pd.DataFrame(data=data, columns=["UMAP1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            if by is not None:
                result_df = pd.concat([result_df, df[[by]]], axis=1)

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="UMAP1",
                    y="N",
                    color=by,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 2:
            title = "UMAP (2D)"
            result_df = pd.DataFrame(data=data, columns=["UMAP1", "UMAP2"])
            if by is not None:
                result_df = pd.concat([result_df, df[[by]]], axis=1)

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="UMAP1",
                    y="UMAP2",
                    color=by,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 3:
            title = "UMAP (3D)"

            result_df = pd.DataFrame(data=data, columns=["UMAP1", "UMAP2", "UMAP3"])
            if by is not None:
                result_df = pd.concat([result_df, df[[by]]], axis=1)

            figure, ax = plt.subplots(
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
                        result_df.loc[mask, "UMAP1"],
                        result_df.loc[mask, "UMAP2"],
                        result_df.loc[mask, "UMAP3"],
                        c=c,
                        label=group,
                    )
                ax.legend(title=by)
            else:
                ax.scatter(
                    data=result_df,
                    xs="UMAP1",
                    ys="UMAP2",
                    zs="UMAP3",
                )

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
