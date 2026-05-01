from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from matplotlib import rcParams
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class MdsResult:
    report: str


def get_mds_result(
    datatable: Datatable,
    variables: list[str],
    factor_name: str,
    n_components: int,
    max_iterations: int,
    metric: str,
    figsize: tuple[float, float] | None = None,
) -> MdsResult:
    columns = [factor_name] + variables
    df = datatable.get_filtered_df(columns)

    # Cleaning
    df.dropna(inplace=True)

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[variables])

    tsne = MDS(
        n_components=n_components,
        max_iter=max_iterations,
        metric=metric,
    )
    data = tsne.fit_transform(scaled_data)

    if figsize is None:
        figsize = rcParams["figure.figsize"]

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    match n_components:
        case 1:
            title = "Multidimensional Scaling (1D)"
            result_df = pd.DataFrame(data=data, columns=["MDS1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="MDS1",
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
            title = "Multidimensional Scaling (2D)"

            result_df = pd.DataFrame({
                "MDS1": data[:, 0],
                "MDS2": data[:, 1],
            })
            result_df[factor_name] = df[factor_name].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="MDS1",
                    y="MDS2",
                    color=factor_name,
                )
                .add(so.Dot(pointsize=3))
                .scale(color=palette)
                .label(title=title)
                .on(figure)
                .plot(True)
            )
        case 3:
            title = "Multidimensional Scaling (3D)"

            result_df = pd.DataFrame({
                "MDS1": data[:, 0],
                "MDS2": data[:, 1],
                "MDS3": data[:, 2],
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
                    group_df["MDS1"],
                    group_df["MDS2"],
                    group_df["MDS3"],
                    c=c,
                    label=group,
                )
            ax.legend(title=factor_name)

            ax.set(
                xlabel="MDS1",
                ylabel="MDS2",
                zlabel="MDS3",
                title=title,
            )

    report = get_html_image_from_figure(figure)

    return MdsResult(
        report=report,
    )
