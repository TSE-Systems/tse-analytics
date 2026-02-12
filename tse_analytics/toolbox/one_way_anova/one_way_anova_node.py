from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.enums import EFFECT_SIZE
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.one_way_anova.processor import get_one_way_anova_result


class OneWayAnovaNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "One-way ANOVA"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Dependent variable",
            "Dependent variable",
        )

        self.add_text_input(
            "factor",
            "",
            "",
            "Between-subject factor",
            "Between-subject factor",
        )

        self.add_combo_menu(
            "effect_size",
            "Effect Size",
            items=list(EFFECT_SIZE.keys()),
            tooltip="Effect size type",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        variable_name = str(self.get_property("variable"))
        factor_name = str(self.get_property("factor"))
        effect_size = str(self.get_property("effect_size"))

        columns = datatable.get_default_columns() + list(datatable.dataset.factors) + [variable_name]
        df = datatable.get_filtered_df(columns)

        result = get_one_way_anova_result(
            datatable.dataset,
            df,
            datatable.variables[variable_name],
            factor_name,
            EFFECT_SIZE[effect_size],
        )

        return PipelinePacket(datatable, report=result.report)
