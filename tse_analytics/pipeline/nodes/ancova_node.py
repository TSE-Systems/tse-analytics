from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.ancova.processor import get_ancova_result
from tse_analytics.toolbox.shared import EFFECT_SIZE, P_ADJUSTMENT


class AncovaNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "ANCOVA"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "dependent_variable",
            "",
            "",
            "Dependent variable",
            "Dependent variable",
        )

        self.add_text_input(
            "covariate_variable",
            "",
            "",
            "Covariate",
            "Covariate variable",
        )

        self.add_text_input(
            "factor",
            "",
            "",
            "Factor",
            "Between-subject factor",
        )

        self.add_combo_menu(
            "effect_size",
            "Effect Size",
            items=list(EFFECT_SIZE.keys()),
            tooltip="Effect size type",
        )

        self.add_combo_menu(
            "p_adjustment",
            "P adjustment",
            items=list(P_ADJUSTMENT.keys()),
            tooltip="P-value correction",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        dependent_name = str(self.get_property("dependent_variable")).strip()
        covariate_name = str(self.get_property("covariate_variable")).strip()
        factor_name = str(self.get_property("factor")).strip()
        effect_size_name = str(self.get_property("effect_size"))
        p_adjustment_name = str(self.get_property("p_adjustment"))

        if not dependent_name:
            return PipelinePacket.inactive(reason="No dependent variable selected")

        if not covariate_name:
            return PipelinePacket.inactive(reason="No covariate variable selected")

        if not factor_name:
            return PipelinePacket.inactive(reason="No factor selected")

        dependent_variable = datatable.variables.get(dependent_name)
        if dependent_variable is None:
            return PipelinePacket.inactive(reason="Invalid dependent variable")

        covariate_variable = datatable.variables.get(covariate_name)
        if covariate_variable is None:
            return PipelinePacket.inactive(reason="Invalid covariate variable")

        if factor_name not in datatable.dataset.factors:
            return PipelinePacket.inactive(reason="Invalid factor selected")

        effect_size = EFFECT_SIZE.get(effect_size_name)
        if effect_size is None:
            return PipelinePacket.inactive(reason="Invalid effect size selection")

        p_adjustment = P_ADJUSTMENT.get(p_adjustment_name)
        if p_adjustment is None:
            return PipelinePacket.inactive(reason="Invalid p-adjustment selection")

        columns = datatable.get_default_columns() + list(datatable.dataset.factors) + [dependent_name, covariate_name]
        df = datatable.get_filtered_df(columns)

        result = get_ancova_result(
            datatable.dataset,
            df,
            dependent_variable,
            covariate_variable,
            factor_name,
            effect_size,
            p_adjustment,
        )

        return PipelinePacket(datatable, report=result.report)
