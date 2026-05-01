from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class TsneResult:
    report: str


def get_tsne_result(
    datatable: Datatable,
    variables: list[str],
    factor_name: str,
    n_components: int,
    perplexity: int,
    max_iterations: int,
    metric: str,
    figsize: tuple[float, float] | None = None,
) -> TsneResult:
    columns = [factor_name] + variables
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

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

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    match n_components:
        case 1:
            title = "t-SNE (1D)"
            result_df = pd.DataFrame(data=data, columns=["t-SNE1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="t-SNE1",
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
            title = "t-SNE (2D)"

            result_df = pd.DataFrame({
                "t-SNE1": data[:, 0],
                "t-SNE2": data[:, 1],
            })
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="t-SNE1",
                    y="t-SNE2",
                    color=factor_name,
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
                    group_df["t-SNE1"],
                    group_df["t-SNE2"],
                    group_df["t-SNE3"],
                    c=c,
                    label=group,
                )
            ax.legend(title=factor_name)

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
