from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import pingouin as pg
import seaborn.objects as so
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure
from tse_analytics.core.utils.data import group_df_by_animal


@dataclass
class RegressionResult:
    report: str


def get_regression_result(
    dataset: Dataset,
    df: pd.DataFrame,
    covariate: Variable,
    response: Variable,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> RegressionResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    # Create a figure with a tight layout
    figure = plt.Figure(figsize=figsize, layout="tight")

    # Group by animal
    df = group_df_by_animal(
        df,
        {
            covariate.name: covariate,
            response.name: response,
        },
    )

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            by = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case GroupingMode.RUN:
            by = "Run"
            palette = color_manager.get_run_to_color_dict(dataset.runs)
        case GroupingMode.FACTOR:
            by = grouping_settings.factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[by])
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

    match grouping_settings.mode:
        case GroupingMode.ANIMAL:
            output = ""
        case GroupingMode.FACTOR:
            output = ""
            for level in df[grouping_settings.factor_name].unique().tolist():
                data = df[df[grouping_settings.factor_name] == level]
                output = (
                    output
                    + get_great_table(
                        pg.linear_regression(data[covariate.name], data[response.name], remove_na=True),
                        f"Level: {level}",
                    ).as_raw_html(inline_css=True)
                    + "<p>"
                )
        case GroupingMode.RUN:
            output = ""
            for run in df["Run"].unique().tolist():
                data = df[df["Run"] == run]
                output = (
                    output
                    + get_great_table(
                        pg.linear_regression(data[covariate.name], data[response.name], remove_na=True),
                        f"Run: {run}",
                    ).as_raw_html(inline_css=True)
                    + "<p>"
                )
        case _:
            data = df
            output = get_great_table(
                pg.linear_regression(data[covariate.name], data[response.name], remove_na=True),
                "Total",
            ).as_raw_html(inline_css=True)

    report = f"""
    {output}
    <p>
    {get_html_image_from_figure(figure)}
    """

    return RegressionResult(
        report=report,
    )
