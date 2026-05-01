from dataclasses import dataclass

import matplotlib.pyplot as plt
import pingouin as pg
import seaborn.objects as so
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure


@dataclass
class RegressionResult:
    report: str


def get_regression_result(
    datatable: Datatable,
    covariate: Variable,
    response: Variable,
    factor_name: str,
    figsize: tuple[float, float] | None = None,
) -> RegressionResult:
    columns = [response.name] if response.name == covariate.name else [covariate.name, response.name]
    columns = ["Animal", factor_name] + columns
    df = datatable.get_filtered_df(columns)
    df = (
        df
        .groupby(
            ["Animal", factor_name],
            dropna=False,
            observed=True,
        )
        .aggregate({
            covariate.name: covariate.aggregation,
            response.name: response.aggregation,
        })
        .reset_index()
    )

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])

    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = plt.Figure(figsize=figsize, layout="tight")

    (
        so
        .Plot(
            df,
            x=covariate.name,
            y=response.name,
            color=factor_name,
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

    output = ""
    for level in df[factor_name].unique().tolist():
        data = df[df[factor_name] == level]
        output = (
            output
            + get_great_table(
                pg.linear_regression(data[covariate.name], data[response.name], remove_na=True),
                f"Level: {level}",
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
