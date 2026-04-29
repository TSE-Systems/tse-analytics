from dataclasses import dataclass

import pingouin as pg
import seaborn as sns
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure
from tse_analytics.core.utils.data import get_columns_by_grouping_settings


@dataclass
class CorrelationResult:
    report: str


def get_correlation_result(
    datatable: Datatable,
    x_var_name: str,
    y_var_name: str,
    grouping_settings: GroupingSettings,
    figsize: tuple[float, float] | None = None,
) -> CorrelationResult:
    variable_columns = [x_var_name] if x_var_name == y_var_name else [x_var_name, y_var_name]
    columns = get_columns_by_grouping_settings(grouping_settings, variable_columns)
    df = datatable.get_filtered_df(columns)

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

    if grouping_settings.mode != GroupingMode.TOTAL and grouping_settings.mode != GroupingMode.RUN:
        df[by] = df[by].cat.remove_unused_categories()

    if figsize is None:
        figsize = rcParams["figure.figsize"]

    joint_grid = sns.jointplot(
        data=df,
        x=x_var_name,
        y=y_var_name,
        hue=by,
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
