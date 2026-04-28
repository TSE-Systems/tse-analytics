from dataclasses import dataclass

import pingouin as pg

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table


@dataclass
class AncovaResult:
    report: str


def get_ancova_result(
    datatable: Datatable,
    dependent_variable: Variable,
    covariate_variable: Variable,
    factor_name: str,
    effsize: str,
    padjust: str,
) -> AncovaResult:
    df = datatable.get_filtered_df(["Animal", dependent_variable.name, covariate_variable.name, factor_name])
    df = (
        df
        .groupby(
            ["Animal", factor_name],
            dropna=False,
            observed=True,
        )
        .aggregate({
            dependent_variable.name: dependent_variable.aggregation,
            covariate_variable.name: covariate_variable.aggregation,
        })
        .reset_index()
    )

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
