from dataclasses import dataclass

import pandas as pd
import pingouin as pg

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_table


@dataclass
class NWayAnovaResult:
    report: str


def get_n_way_anova_result(
    dataset: Dataset,
    df: pd.DataFrame,
    dependent_variable: Variable,
    factor_names: list[str],
    effsize: str,
    padjust: str,
) -> NWayAnovaResult:
    # Binning
    df = process_time_interval_binning(
        df,
        TimeIntervalsBinningSettings("day", 365),
        {
            dependent_variable.name: dependent_variable,
        },
        origin=dataset.experiment_started,
    )

    # TODO: should or should not?
    df.dropna(inplace=True)

    # Sanitize variable name: comma, bracket, and colon are not allowed in column names
    sanitized_dependent_variable = dependent_variable.name.replace("(", "_").replace(")", "").replace(",", "_")
    if sanitized_dependent_variable != dependent_variable.name:
        df.rename(columns={dependent_variable.name: sanitized_dependent_variable}, inplace=True)

    anova = pg.anova(
        data=df,
        dv=dependent_variable.name,
        between=factor_names,
        detailed=True,
    )

    html_template = """
                    {anova}
                    """

    match len(factor_names):
        case 2:
            anova_header = "Two-way ANOVA"
        case 3:
            anova_header = "Three-way ANOVA"
        case _:
            anova_header = "Multi-way ANOVA"

    if len(factor_names) > 2:
        report = html_template.format(
            anova=get_html_table(anova, anova_header, index=False),
        )
    else:
        post_hoc_test = pg.pairwise_tests(
            data=df,
            dv=dependent_variable.name,
            between=factor_names,
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
            nan_policy="listwise",
        )

        html_template += """
                        {post_hoc_test}
                        """

        report = html_template.format(
            anova=get_html_table(anova, anova_header, index=False),
            post_hoc_test=get_html_table(post_hoc_test, "Pairwise post-hoc tests", index=False),
        )

    return NWayAnovaResult(
        report=report,
    )
