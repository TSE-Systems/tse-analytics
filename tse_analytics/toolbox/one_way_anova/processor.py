from dataclasses import dataclass

import pingouin as pg
from matplotlib import rcParams
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_figure


@dataclass
class OneWayAnovaResult:
    report: str


def get_one_way_anova_result(
    datatable: Datatable,
    dependent_variable: Variable,
    factor_name: str,
    effsize: str,
    figsize: tuple[float, float] | None = None,
) -> OneWayAnovaResult:
    df = datatable.get_filtered_df(["Animal", dependent_variable.name, factor_name])
    df = (
        df
        .groupby(
            ["Animal", factor_name],
            dropna=False,
            observed=True,
        )
        .aggregate({
            dependent_variable.name: dependent_variable.aggregation,
        })
        .reset_index()
    )

    normality = pg.normality(df, group=factor_name, dv=dependent_variable.name)
    homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=dependent_variable.name)

    if homoscedasticity.loc["levene"]["equal_var"]:
        anova = pg.anova(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
            detailed=True,
        )
        anova_header = "One-way classic ANOVA"

        post_hoc_test = pg.pairwise_tukey(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
            effsize=effsize,
        )
        post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
    else:
        anova = pg.welch_anova(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
        )
        anova_header = "One-way Welch ANOVA"

        post_hoc_test = pg.pairwise_gameshowell(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
            effsize=effsize,
        )
        post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

    pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[dependent_variable.name], df[factor_name])
    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = pairwise_tukeyhsd_res.plot_simultaneous(
        ylabel="Level",
        xlabel=dependent_variable.name,
        figsize=(figsize[0], figsize[0] / 2),
    )

    html_template = """
                    <h2>Factor: {factor_name}</h2>
                    {normality}
                    <p>
                    {homoscedasticity}
                    <p>
                    {anova}
                    <p>
                    {post_hoc_test}
                    <p>
                    {image}
                    """

    report = html_template.format(
        factor_name=factor_name,
        anova=get_great_table(anova, anova_header).as_raw_html(inline_css=True),
        normality=get_great_table(
            normality.reset_index(), "Univariate normality test", rowname_col=normality.index.name
        ).as_raw_html(inline_css=True),
        homoscedasticity=get_great_table(
            homoscedasticity.reset_index(),
            "Homoscedasticity (equality of variances)",
            rowname_col=homoscedasticity.index.name,
        ).as_raw_html(inline_css=True),
        post_hoc_test=get_great_table(post_hoc_test, post_hoc_test_header).as_raw_html(inline_css=True),
        image=get_html_image_from_figure(figure),
    )

    return OneWayAnovaResult(
        report=report,
    )
