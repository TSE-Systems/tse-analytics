from dataclasses import dataclass

import pandas as pd
import pingouin as pg
from matplotlib import rcParams
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_image_from_figure, get_html_table


@dataclass
class OneWayAnovaResult:
    report: str


def get_one_way_anova_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable: Variable,
    factor_name: str,
    effsize: str,
    figsize: tuple[float, float] | None = None,
) -> OneWayAnovaResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    # Binning
    df = process_time_interval_binning(
        df,
        TimeIntervalsBinningSettings("day", 365),
        {
            variable.name: variable,
        },
        origin=dataset.experiment_started,
    )

    # TODO: should or should not?
    df.dropna(inplace=True)

    normality = pg.normality(df, group=factor_name, dv=variable.name)
    homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=variable.name)

    if homoscedasticity.loc["levene"]["equal_var"]:
        anova = pg.anova(
            data=df,
            dv=variable.name,
            between=factor_name,
            detailed=True,
        )
        anova_header = "One-way classic ANOVA"

        post_hoc_test = pg.pairwise_tukey(
            data=df,
            dv=variable.name,
            between=factor_name,
            effsize=effsize,
        )
        post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
    else:
        anova = pg.welch_anova(
            data=df,
            dv=variable.name,
            between=factor_name,
        )
        anova_header = "One-way Welch ANOVA"

        post_hoc_test = pg.pairwise_gameshowell(
            data=df,
            dv=variable.name,
            between=factor_name,
            effsize=effsize,
        )
        post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

    pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[variable.name], df[factor_name])
    figure = pairwise_tukeyhsd_res.plot_simultaneous(
        ylabel="Level",
        xlabel=variable.name,
        figsize=(figsize[0], figsize[0] / 2),
    )

    html_template = """
                    <h2>Factor: {factor_name}</h2>
                    {normality}
                    {homoscedasticity}
                    {anova}
                    {post_hoc_test}
                    {image}
                    """

    report = html_template.format(
        factor_name=factor_name,
        anova=get_html_table(anova, anova_header, index=False),
        normality=get_html_table(normality, "Univariate normality test"),
        homoscedasticity=get_html_table(homoscedasticity, "Homoscedasticity (equality of variances)"),
        post_hoc_test=get_html_table(post_hoc_test, post_hoc_test_header, index=False),
        image=get_html_image_from_figure(figure),
    )

    return OneWayAnovaResult(
        report=report,
    )
