from dataclasses import dataclass

import matplotlib.pyplot as plt
import pingouin as pg
import seaborn.objects as so
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class RegressionResult:
    report: str


def get_regression_result(
    datatable: Datatable,
    covariate: Variable,
    response: Variable,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> RegressionResult:
    columns = [response.name] if response.name == covariate.name else [covariate.name, response.name]
    columns = ["Animal"] + get_columns_by_grouping_settings(grouping_settings, columns)
    df = datatable.get_filtered_df(columns)
    df = (
        df
        .groupby(
            ["Animal"] + get_columns_by_grouping_settings(grouping_settings, []),
            dropna=False,
            observed=True,
        )
        .aggregate({
            covariate.name: covariate.aggregation,
            response.name: response.aggregation,
        })
        .reset_index()
    )

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

    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = plt.Figure(figsize=figsize, layout="tight")

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

    report = f"""
    {output}
    <p>
    {get_html_image_from_figure(figure)}
    """

    return RegressionResult(
        report=report,
    )
