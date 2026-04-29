from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class TsneResult:
    report: str


def get_tsne_result(
    datatable: Datatable,
    variables: list[str],
    grouping_settings: GroupingSettings,
    n_components: int,
    perplexity: int,
    max_iterations: int,
    metric: str,
    figsize: tuple[float, float] | None = None,
) -> TsneResult:
    columns = get_columns_by_grouping_settings(grouping_settings, variables)
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(datatable.dataset.animals)
        case GroupingMode.RUN:
            by = "Run"
            palette = color_manager.get_run_to_color_dict(datatable.dataset.runs)
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[by])
        case _:
            by = None
            palette = color_manager.colormap_name

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[variables])

    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        max_iter=max_iterations,
        metric=metric,
        init="pca",
    )
    data = tsne.fit_transform(scaled_data)

    match n_components:
        case 1:
            title = "t-SNE (1D)"
            result_df = pd.DataFrame(data=data, columns=["t-SNE1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            if by is not None:
                result_df[by] = df[by].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="t-SNE1",
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
            title = "t-SNE (2D)"

            result_df = pd.DataFrame({
                "t-SNE1": data[:, 0],
                "t-SNE2": data[:, 1],
            })
            if by is not None:
                result_df[by] = df[by].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="t-SNE1",
                    y="t-SNE2",
                    color=by,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 3:
            title = "t-SNE (3D)"

            result_df = pd.DataFrame({
                "t-SNE1": data[:, 0],
                "t-SNE2": data[:, 1],
                "t-SNE3": data[:, 2],
            })
            if by is not None:
                result_df[by] = df[by].values

            figure, ax = plt.subplots(
                1,
                1,
                figsize=(figsize[0], figsize[0]),
                layout="tight",
                subplot_kw={"projection": "3d"},
            )

            if by is not None:
                for group, c in palette.items():
                    group_df = result_df[result_df[by] == group]
                    ax.scatter(
                        group_df["t-SNE1"],
                        group_df["t-SNE2"],
                        group_df["t-SNE3"],
                        c=c,
                        label=group,
                    )
                ax.legend(title=by)
            else:
                ax.scatter(
                    data=result_df,
                    xs="t-SNE1",
                    ys="t-SNE2",
                    zs="t-SNE3",
                )

            ax.set(
                xlabel="t-SNE1",
                ylabel="t-SNE2",
                zlabel="t-SNE3",
                title=title,
            )

    report = get_html_image_from_figure(figure)

    return TsneResult(
        report=report,
    )
