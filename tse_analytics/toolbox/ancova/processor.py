from dataclasses import dataclass

import pandas as pd
import pingouin as pg

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table


@dataclass
class AncovaResult:
    report: str


def get_ancova_result(
    dataset: Dataset,
    df: pd.DataFrame,
    dependent_variable: Variable,
    covariate_variable: Variable,
    factor_name: str,
    effsize: str,
    padjust: str,
) -> AncovaResult:
    # Binning
    df = process_time_interval_binning(
        df,
        TimeIntervalsBinningSettings("day", 365),
        {
            dependent_variable.name: dependent_variable,
            covariate_variable.name: covariate_variable,
        },
        origin=dataset.experiment_started,
    )

    # TODO: should or should not?
    df.dropna(inplace=True)

    ancova = pg.ancova(
        data=df,
        dv=dependent_variable.name,
        covar=covariate_variable.name,
        between=factor_name,
    )

    pairwise_tests = pg.pairwise_tests(
        data=df,
        dv=dependent_variable.name,
        between=factor_name,
        effsize=effsize,
        padjust=padjust,
        return_desc=True,
    )

    html_template = """
                    {ancova}
                    {pairwise_tests}
                    """

    report = html_template.format(
        ancova=get_great_table(ancova, "ANCOVA").as_raw_html(inline_css=True),
        pairwise_tests=get_great_table(pairwise_tests, "Pairwise post-hoc tests").as_raw_html(inline_css=True),
    )

    return AncovaResult(
        report=report,
    )
