from dataclasses import dataclass

import pingouin as pg
import seaborn as sns
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure


@dataclass
class CorrelationResult:
    report: str


def get_correlation_result(
    datatable: Datatable,
    x_var_name: str,
    y_var_name: str,
    factor_name: str,
    figsize: tuple[float, float] | None = None,
) -> CorrelationResult:
    variable_columns = [x_var_name] if x_var_name == y_var_name else [x_var_name, y_var_name]
    columns = variable_columns + [factor_name]
    df = datatable.get_filtered_df(columns)

    df[factor_name] = df[factor_name].cat.remove_unused_categories()

    if figsize is None:
        figsize = rcParams["figure.figsize"]

    palette = color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_name])
    joint_grid = sns.jointplot(
        data=df,
        x=x_var_name,
        y=y_var_name,
        hue=factor_name,
        palette=palette,
        marker=".",
        height=figsize[1],
    )
    joint_grid.figure.set_layout_engine("tight")
    joint_grid.figure.suptitle(f"Correlation between {x_var_name} and {y_var_name}")

    t_test = pg.ttest(df[x_var_name], df[y_var_name])
    corr = pg.pairwise_corr(data=df, columns=[x_var_name, y_var_name], method="pearson")

    report = f"""
    {get_great_table(t_test, "t-test").as_raw_html(inline_css=True)}
    <p>
    {get_great_table(corr, "Pearson correlation").as_raw_html(inline_css=True)}
    <p>
    {get_html_image_from_figure(joint_grid.figure)}
    """

    return CorrelationResult(
        report=report,
    )
