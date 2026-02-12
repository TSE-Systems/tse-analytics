from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.n_way_anova.processor import get_n_way_anova_result


class NWayAnovaNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "N-way ANOVA"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Dependent variable",
            "Dependent variable to test",
        )

        self.add_text_input(
            "factors",
            "",
            "",
            "Factors (comma-separated)",
            "Factor names separated by commas",
        )

        self.add_combo_menu(
            "effect_size",
            "Effect Size",
            items=list(EFFECT_SIZE.keys()),
            tooltip="Effect size type",
        )

        self.add_combo_menu(
            "p_adjustment",
            "P Adjustment",
            items=list(P_ADJUSTMENT.keys()),
            tooltip="P-value adjustment method",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        variable_name = str(self.get_property("variable")).strip()
        if not variable_name:
            return PipelinePacket.inactive(reason="No dependent variable specified")

        # Get dependent variable from datatable
        variable = datatable.variables.get(variable_name)
        if variable is None:
            return PipelinePacket.inactive(reason=f"Variable '{variable_name}' not found")

        # Parse factor names from comma-separated string
        factors_str = str(self.get_property("factors")).strip()
        if not factors_str:
            return PipelinePacket.inactive(reason="No factors specified")

        factor_names = [f.strip() for f in factors_str.split(",") if f.strip()]
        if len(factor_names) < 2:
            return PipelinePacket.inactive(reason="At least 2 factors required for N-way ANOVA")

        # Get effect size and p-adjustment settings
        effect_size_label = str(self.get_property("effect_size"))
        p_adjustment_label = str(self.get_property("p_adjustment"))

        effect_size = EFFECT_SIZE.get(effect_size_label, "none")
        p_adjustment = P_ADJUSTMENT.get(p_adjustment_label, "none")

        # Get filtered dataframe with necessary columns
        columns = datatable.get_default_columns() + list(datatable.dataset.factors) + [variable_name]
        df = datatable.get_filtered_df(columns)

        # Perform N-way ANOVA analysis
        result = get_n_way_anova_result(
            datatable.dataset,
            df,
            variable,
            factor_names,
            effect_size,
            p_adjustment,
        )

        return PipelinePacket(datatable, report=result.report)
