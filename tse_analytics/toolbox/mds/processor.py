from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn.objects as so
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class MdsResult:
    report: str


def get_mds_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variables: list[str],
    split_mode: SplitMode,
    factor_name: str | None,
    max_iterations: int,
    figsize: tuple[float, float] | None = None,
) -> MdsResult:
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

    tsne = MDS(
        n_components=2,
        max_iter=max_iterations,
        random_state=0,
    )
    data = tsne.fit_transform(scaled_data)
    title = "Multidimensional Scaling (MDS)"

    result_df = pd.DataFrame(data=data, columns=["MDS1", "MDS2"])
    if by is not None:
        result_df = pd.concat([result_df, df[[by]]], axis=1)

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

    report = get_html_image_from_figure(figure)

    return MdsResult(
        report=report,
    )
