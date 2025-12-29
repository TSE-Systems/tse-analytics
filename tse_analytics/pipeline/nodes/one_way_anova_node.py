import pingouin as pg
from NodeGraphQt.widgets.node_widgets import NodeComboBox
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core import manager
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.utils import get_html_image_from_figure, get_html_table
from tse_analytics.pipeline import PipelineNode
from tse_analytics.toolbox.shared import EFFECT_SIZE


class OneWayAnovaNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "One-way ANOVA"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_combo_menu(
            "variable",
            "Variable",
            items=[],
            tooltip="Dependent variable",
        )

        self.add_combo_menu(
            "factor",
            "Factor",
            items=[],
            tooltip="Factor for grouping",
        )

        self.add_combo_menu(
            "effsize",
            "Effect Size",
            items=list(EFFECT_SIZE.keys()),
            tooltip="Effect size type",
        )

    def initialize(self, dataset: Dataset):
        datatable = manager.get_selected_datatable()

        # Initialize variable selector
        if datatable is None:
            variable_names = ["No variables"]
            factor_names = ["No factors"]
        else:
            variable_names = list(datatable.variables.keys())
            factor_names = list(datatable.dataset.factors.keys())

        variable_widget: NodeComboBox = self.get_widget("variable")
        variable_widget.clear()
        variable_widget.add_items(variable_names)

        factor_widget: NodeComboBox = self.get_widget("factor")
        factor_widget.clear()
        factor_widget.add_items(factor_names)

        effsize_widget: NodeComboBox = self.get_widget("effsize")
        effsize_widget.set_value("Hedges g")

    def process(self, datatable: Datatable):
        """
        Perform one-way ANOVA analysis and return HTML report.
        """
        if datatable is None or not isinstance(datatable, Datatable):
            return None

        variable_name = str(self.get_property("variable"))
        factor_name = str(self.get_property("factor"))
        effsize_type = str(self.get_property("effsize"))

        if variable_name == "No variables" or factor_name == "No factors":
            return None

        dependent_variable = datatable.variables.get(variable_name)
        if dependent_variable is None:
            return None

        variables = {variable_name: dependent_variable}

        columns = datatable.get_default_columns() + list(datatable.dataset.factors) + list(variables)
        df = datatable.get_filtered_df(columns)

        # Binning
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            variables,
            origin=datatable.dataset.experiment_started,
        )

        # Drop missing values
        df.dropna(inplace=True)

        effsize = EFFECT_SIZE[effsize_type]

        # Normality and homoscedasticity tests
        normality = pg.normality(df, group=factor_name, dv=variable_name)
        homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=variable_name)

        # Choose appropriate ANOVA test based on homoscedasticity
        if homoscedasticity.loc["levene"]["equal_var"]:
            anova = pg.anova(
                data=df,
                dv=variable_name,
                between=factor_name,
                detailed=True,
            )
            anova_header = "One-way classic ANOVA"

            post_hoc_test = pg.pairwise_tukey(
                data=df,
                dv=variable_name,
                between=factor_name,
                effsize=effsize,
            )
            post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
        else:
            anova = pg.welch_anova(
                data=df,
                dv=variable_name,
                between=factor_name,
            )
            anova_header = "One-way Welch ANOVA"

            post_hoc_test = pg.pairwise_gameshowell(
                data=df,
                dv=variable_name,
                between=factor_name,
                effsize=effsize,
            )
            post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

        # Generate plot
        pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[variable_name], df[factor_name])
        figure = pairwise_tukeyhsd_res.plot_simultaneous(ylabel="Level", xlabel=variable_name)
        img_html = get_html_image_from_figure(figure)
        figure.clear()

        # Generate HTML report
        html_template = """
        <h2>Factor: {factor_name}</h2>
        {normality}
        {homoscedasticity}
        {anova}
        {post_hoc_test}
        {img_html}
        """

        html = html_template.format(
            factor_name=factor_name,
            anova=get_html_table(anova, anova_header, index=False),
            normality=get_html_table(normality, "Univariate normality test"),
            homoscedasticity=get_html_table(homoscedasticity, "Homoscedasticity (equality of variances)"),
            post_hoc_test=get_html_table(post_hoc_test, post_hoc_test_header, index=False),
            img_html=img_html,
        )

        # Update tooltip with summary
        p_value = anova.loc[0, "p-unc"] if "p-unc" in anova.columns else anova.loc[0, "p-unc"]
        tooltip = (
            f"<b>One-way ANOVA</b><br/>Variable: {variable_name}<br/>Factor: {factor_name}<br/>P-value: {p_value:.5f}"
        )
        self.view.setToolTip(tooltip)

        return html
