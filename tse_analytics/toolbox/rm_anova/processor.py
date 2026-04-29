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
class RMAnovaResult:
    report: str


def get_rm_anova_result(
    datatable: Datatable,
    dependent_variable: Variable,
    factor_names: list[str],
    do_pairwise_tests: bool,
    effsize: str,
    padjust: str,
    figsize: tuple[float, float] | None = None,
) -> RMAnovaResult:
    subject = datatable.dataset.subject_id_column
    df = datatable.get_filtered_df([subject, dependent_variable.name] + factor_names)
    df = (
        df
        .groupby(
            [subject] + factor_names,
            dropna=False,
            observed=True,
        )
        .aggregate({
            dependent_variable.name: dependent_variable.aggregation,
        })
        .reset_index()
    )

    report_sections: list[str] = []
    for factor_name in factor_names:
        spher, W, chisq, dof, pval = pg.sphericity(
            data=df,
            dv=dependent_variable.name,
            within=factor_name,
            subject=subject,
            method="mauchly",
        )
        sphericity = pd.DataFrame(
            [[spher, W, chisq, dof, pval]],
            columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
        )
        report_sections.append(
            get_great_table(sphericity, f"Sphericity Test: {factor_name}").as_raw_html(inline_css=True)
        )

    anova = pg.rm_anova(
        data=df,
        dv=dependent_variable.name,
        within=factor_names,
        subject=subject,
        detailed=True,
    )
    report_sections.append(get_great_table(anova, "Repeated measures ANOVA").as_raw_html(inline_css=True))

    if do_pairwise_tests:
        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable.name,
            within=factor_names,
            subject=subject,
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
        )
        report_sections.append(get_great_table(pairwise_tests, "Pairwise post-hoc tests").as_raw_html(inline_css=True))

    plot_kwargs: dict = {"x": factor_names[0], "y": dependent_variable.name}
    if len(factor_names) >= 2:
        plot_kwargs["color"] = factor_names[1]

    if figsize is None:
        figsize = rcParams["figure.figsize"]
    figure = plt.Figure(figsize=(figsize[0], figsize[0] / 2), layout="tight")

    plot = (
        so
        .Plot(df, **plot_kwargs)
        .add(so.Range(), so.Est(errorbar="se"))
        .add(so.Dot(), so.Agg())
        .add(so.Line(), so.Agg())
    )

    if len(factor_names) >= 2:
        plot = plot.scale(color=color_manager.get_level_to_color_dict(datatable.dataset.factors[factor_names[1]]))

    plot = plot.label(title=f"{dependent_variable.name} over {', '.join(factor_names)}").on(figure).plot(True)

    report_sections.append(get_html_image_from_plot(plot))

    report = "\n<p>\n".join(report_sections)

    return RMAnovaResult(
        report=report,
    )
