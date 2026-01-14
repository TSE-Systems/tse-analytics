from dataclasses import dataclass

import pandas as pd
import pingouin as pg
import seaborn as sns

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image_from_figure


@dataclass
class CorrelationResult:
    report: str


def get_correlation_result(
    dataset: Dataset,
    df: pd.DataFrame,
    x_var_name: str,
    y_var_name: str,
    split_mode: SplitMode,
    factor_name: str | None,
    figsize: tuple[float, float] | None = None,
) -> CorrelationResult:
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

    if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
        df[by] = df[by].cat.remove_unused_categories()

    joint_grid = sns.jointplot(
        data=df,
        x=x_var_name,
        y=y_var_name,
        hue=by,
        palette=palette,
        marker=".",
    )
    joint_grid.figure.set_figwidth(figsize[0])
    joint_grid.figure.set_layout_engine("tight")
    joint_grid.figure.suptitle(f"Correlation between {x_var_name} and {y_var_name}")

    t_test = pg.ttest(df[x_var_name], df[y_var_name])
    corr = pg.pairwise_corr(data=df, columns=[x_var_name, y_var_name], method="pearson")

    html_template = """
                <h2>t-test</h2>
                {t_test}
                <h2>Pearson correlation</h2>
                {corr}
                """

    html = html_template.format(
        t_test=t_test.to_html(),
        corr=corr.to_html(),
    )

    report = get_html_image_from_figure(joint_grid.figure)
    report += html

    return CorrelationResult(
        report=report,
    )
