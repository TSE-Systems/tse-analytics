from dataclasses import dataclass

import pandas as pd
import pingouin as pg
import seaborn.objects as so
from matplotlib import pyplot as plt
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_plot


@dataclass
class MixedAnovaResult:
    report: str


def get_mixed_anova_result(
    datatable: Datatable,
    dependent_variable: Variable,
    between_subject_factor_name: str,
    within_subject_factor_name: str,
    do_pairwise_tests: bool,
    effsize: str,
    padjust: str,
    figsize: tuple[float, float] | None = None,
) -> MixedAnovaResult:
    df = datatable.get_filtered_df([
        "Animal",
        between_subject_factor_name,
        within_subject_factor_name,
        dependent_variable.name,
    ])
    df = (
        df
        .groupby(
            ["Animal", between_subject_factor_name, within_subject_factor_name],
            dropna=False,
            observed=True,
        )
        .aggregate({
            dependent_variable.name: dependent_variable.aggregation,
        })
        .reset_index()
    )

    report_sections: list[str] = []

    spher, W, chisq, dof, pval = pg.sphericity(
        data=df,
        dv=dependent_variable.name,
        within=within_subject_factor_name,
        subject="Animal",
        method="mauchly",
    )
    sphericity = pd.DataFrame(
        [[spher, W, chisq, dof, pval]],
        columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
    )
    report_sections.append(
        get_great_table(sphericity, f"Sphericity Test: {within_subject_factor_name}").as_raw_html(inline_css=True)
    )

    anova = pg.mixed_anova(
        data=df,
        dv=dependent_variable.name,
        between=between_subject_factor_name,
        within=within_subject_factor_name,
        subject="Animal",
    )
    report_sections.append(get_great_table(anova, "Mixed-design ANOVA").as_raw_html(inline_css=True))

    if do_pairwise_tests:
        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable.name,
            within=within_subject_factor_name,
            between=between_subject_factor_name,
            subject="Animal",
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
        )
        report_sections.append(get_great_table(pairwise_tests, "Pairwise post-hoc tests").as_raw_html(inline_css=True))

    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = plt.Figure(figsize=(figsize[0], figsize[0] / 2), layout="tight")

    plot = (
        so
        .Plot(
            df,
            x=within_subject_factor_name,
            y=dependent_variable.name,
            color=between_subject_factor_name,
        )
        .add(so.Range(), so.Est(errorbar="se"))
        .add(so.Dot(), so.Agg())
        .add(so.Line(), so.Agg())
        .scale(color=color_manager.get_level_to_color_dict(datatable.dataset.factors[between_subject_factor_name]))
        .label(title=f"{dependent_variable.name} over time")
        .on(figure)
        .plot(True)
    )
    report_sections.append(get_html_image_from_plot(plot))

    report = "\n<p>\n".join(report_sections)

    return MixedAnovaResult(
        report=report,
    )
