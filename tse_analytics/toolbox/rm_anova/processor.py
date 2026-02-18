from dataclasses import dataclass

import pandas as pd
import pingouin as pg
import seaborn.objects as so
from matplotlib import rcParams

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_great_table, get_html_image_from_plot


@dataclass
class RMAnovaResult:
    report: str


def get_rm_anova_result(
    dataset: Dataset,
    df: pd.DataFrame,
    variable: Variable,
    split_mode: SplitMode,
    factor_name: str,
    do_pairwise_tests: bool,
    effsize: str,
    padjust: str,
    figsize: tuple[float, float] | None = None,
) -> RMAnovaResult:
    if figsize is None:
        figsize = rcParams["figure.figsize"]

    match split_mode:
        case SplitMode.ANIMAL:
            subject = "Animal"
            palette = color_manager.get_animal_to_color_dict(dataset.animals)
        case SplitMode.RUN:
            subject = "Run"
            palette = color_manager.colormap_name
        case SplitMode.FACTOR:
            subject = factor_name
            palette = color_manager.get_level_to_color_dict(dataset.factors[factor_name])
        case _:
            # Disabled for Total grouping mode
            subject = None

    spher, W, chisq, dof, pval = pg.sphericity(
        data=df,
        dv=variable.name,
        within="Bin",
        subject=subject,
        method="mauchly",
    )
    sphericity = pd.DataFrame(
        [[spher, W, chisq, dof, pval]],
        columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
    )

    anova = pg.rm_anova(
        data=df,
        dv=variable.name,
        within="Bin",
        subject=subject,
        detailed=True,
    )

    plot = (
        so
        .Plot(
            df,
            x="Bin",
            y=variable.name,
            color=subject if not split_mode == SplitMode.ANIMAL else None,
        )
        .add(so.Range(), so.Est(errorbar="se"))
        .add(so.Dot(), so.Agg())
        .add(so.Line(), so.Agg())
        .scale(color=palette)
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
            subject=subject,
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
        )

        html_template += """
                        {pairwise_tests}
                        """

        report = html_template.format(
            img_html=img_html,
            sphericity=get_great_table(sphericity, "Sphericity Test").as_raw_html(inline_css=True),
            anova=get_great_table(anova, "Repeated measures one-way ANOVA").as_raw_html(inline_css=True),
            pairwise_tests=get_great_table(pairwise_tests, "Pairwise post-hoc tests").as_raw_html(inline_css=True),
        )
    else:
        report = html_template.format(
            img_html=img_html,
            sphericity=get_great_table(sphericity, "Sphericity Test").as_raw_html(inline_css=True),
            anova=get_great_table(anova, "Repeated measures one-way ANOVA").as_raw_html(inline_css=True),
        )

    return RMAnovaResult(
        report=report,
    )
