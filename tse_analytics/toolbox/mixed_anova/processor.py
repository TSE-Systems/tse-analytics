from dataclasses import dataclass

import pandas as pd
import pingouin as pg
import seaborn.objects as so

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_image_from_plot, get_html_table


@dataclass
class MixedAnovaResult:
    report: str


def get_mixed_anova_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable: Variable,
    factor_name: str,
    do_pairwise_tests: bool,
    effsize: str,
    padjust: str,
    figsize: tuple[float, float] | None = None,
) -> MixedAnovaResult:
    anova = pg.mixed_anova(
        data=df,
        dv=variable.name,
        between=factor_name,
        within="Bin",
        subject="Animal",
    )

    spher, W, chisq, dof, pval = pg.sphericity(
        data=df,
        dv=variable.name,
        within="Bin",
        subject="Animal",
        method="mauchly",
    )
    sphericity = pd.DataFrame(
        [[spher, W, chisq, dof, pval]],
        columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
    )

    plot = (
        so
        .Plot(
            df,
            x="Bin",
            y=variable.name,
            color=factor_name,
        )
        .add(so.Range(), so.Est(errorbar="se"))
        .add(so.Dot(), so.Agg())
        .add(so.Line(), so.Agg())
        .scale(color=color_manager.get_level_to_color_dict(dataset.factors[factor_name]))
        .label(title=f"{variable.name} over time")
        .layout(size=(figsize[0], figsize[0] / 2))
    )
    img_html = get_html_image_from_plot(plot)

    html_template = """
                    {img_html}
                    {sphericity}
                    {anova}
                    """

    if do_pairwise_tests:
        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=variable.name,
            within="Bin",
            between=factor_name,
            subject="Animal",
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
        )

        html_template += """
                        {pairwise_tests}
                        """

        report = html_template.format(
            img_html=img_html,
            sphericity=get_html_table(sphericity, "Sphericity Test", index=False),
            anova=get_html_table(anova, "Mixed-design ANOVA", index=False),
            pairwise_tests=get_html_table(pairwise_tests, "Pairwise post-hoc tests", index=False),
        )
    else:
        report = html_template.format(
            img_html=img_html,
            sphericity=get_html_table(sphericity, "Sphericity Test", index=False),
            anova=get_html_table(anova, "Mixed-design ANOVA", index=False),
        )

    return MixedAnovaResult(
        report=report,
    )
