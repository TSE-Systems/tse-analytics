from dataclasses import dataclass

import pingouin as pg

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table


@dataclass
class NWayAnovaResult:
    report: str


def get_n_way_anova_result(
    datatable: Datatable,
    dependent_variable: Variable,
    factor_names: list[str],
    effsize: str,
    padjust: str,
) -> NWayAnovaResult:
    df = datatable.get_filtered_df(["Animal", dependent_variable.name] + factor_names)
    df = (
        df
        .groupby(
            ["Animal"] + factor_names,
            dropna=False,
            observed=True,
        )
        .aggregate({
            dependent_variable.name: dependent_variable.aggregation,
        })
        .reset_index()
    )

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
            anova=get_great_table(anova, anova_header).as_raw_html(inline_css=True),
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
                        <p>
                        {post_hoc_test}
                        """

        report = html_template.format(
            anova=get_great_table(anova, anova_header)
            .data_color(columns=["p-unc"], palette=["white", "red"], domain=[0, 1], na_color="white")
            .as_raw_html(inline_css=True),
            post_hoc_test=get_great_table(post_hoc_test, "Pairwise post-hoc tests").as_raw_html(inline_css=True),
        )

    return NWayAnovaResult(
        report=report,
    )
