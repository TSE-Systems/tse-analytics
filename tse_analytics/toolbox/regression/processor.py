from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import pingouin as pg
import seaborn.objects as so
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class RegressionResult:
    report: str


def get_regression_result(
    dataset: Dataset,
    df: pd.DataFrame,
    covariate: Variable,
    response: Variable,
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> RegressionResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=(figsize[0], figsize[0] / 2), layout="tight")

    # Group by animal
    df = process_time_interval_binning(
        df,
        TimeIntervalsBinningSettings("day", 365),
        {
            covariate.name: covariate,
            response.name: response,
        },
        origin=dataset.experiment_started,
    )

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

    (
        so
        .Plot(
            df,
            x=covariate.name,
            y=response.name,
            color=by,
        )
        .add(so.Dot())
        .add(
            so.Line(),  # adds the regression line
            so.PolyFit(order=1),
        )
        .scale(color=palette)
        .on(figure)
        .plot(True)
    )

    match split_mode:
        case SplitMode.ANIMAL:
            output = ""
        case SplitMode.FACTOR:
            output = ""
            for level in df[factor_name].unique().tolist():
                data = df[df[factor_name] == level]
                output = (
                    output
                    + f"<h3>Level: {level}</h3>"
                    + pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html(
                        index=False
                    )
                )
        case SplitMode.RUN:
            output = ""
            for run in df["Run"].unique().tolist():
                data = df[df["Run"] == run]
                output = (
                    output
                    + f"<h3>Run: {run}</h3>"
                    + pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html(
                        index=False
                    )
                )
        case _:
            data = df
            output = pg.linear_regression(data[covariate.name], data[response.name], remove_na=True).to_html(
                index=False
            )

    html_template = """
                    <h2>Linear Regression</h2>
                    {output}
                    """

    html = html_template.format(
        output=output,
    )

    report = get_html_image_from_figure(figure)
    report += html

    return RegressionResult(
        report=report,
    )
