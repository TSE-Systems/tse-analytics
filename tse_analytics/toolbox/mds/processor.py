from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from matplotlib import rcParams
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class MdsResult:
    report: str


def get_mds_result(
    datatable: Datatable,
    variables: list[str],
    grouping_settings: GroupingSettings,
    n_components: int,
    max_iterations: int,
    metric: str,
    figsize: tuple[float, float] | None = None,
) -> MdsResult:
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

    match n_components:
        case 1:
            title = "Multidimensional Scaling (1D)"
            result_df = pd.DataFrame(data=data, columns=["MDS1"])
            result_df = pd.concat([result_df, pd.Series(range(len(result_df)), name="N")], axis=1)
            if by is not None:
                result_df[by] = df[by].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="MDS1",
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
            title = "Multidimensional Scaling (2D)"

            result_df = pd.DataFrame({
                "MDS1": data[:, 0],
                "MDS2": data[:, 1],
            })
            if by is not None:
                result_df[by] = df[by].values

            # Create a figure with a tight layout
            figure = plt.Figure(figsize=figsize, layout="tight")
            (
                so
                .Plot(
                    result_df,
                    x="MDS1",
                    y="MDS2",
                    color=by,
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
                        group_df["MDS1"],
                        group_df["MDS2"],
                        group_df["MDS3"],
                        c=c,
                        label=group,
                    )
                ax.legend(title=by)
            else:
                ax.scatter(
                    data=result_df,
                    xs="MDS1",
                    ys="MDS2",
                    zs="MDS3",
                )

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
