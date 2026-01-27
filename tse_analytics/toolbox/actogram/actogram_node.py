from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.pipeline import PipelineNode
from tse_analytics.core.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.actogram.processor import get_actogram_result


class ActogramNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Actogram"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Variable",
            "Variable to plot",
        )

        self.add_text_input(
            "bins_per_hour",
            "",
            "6",
            "Bins per hour",
            "Bins per hour (1-60)",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        variable_name = str(self.get_property("variable")).strip()
        if not variable_name:
            return PipelinePacket.inactive(reason="No variable selected")

        variable = datatable.variables.get(variable_name)
        if variable is None:
            return PipelinePacket.inactive(reason="Invalid variable selected")

        bins_per_hour_raw = str(self.get_property("bins_per_hour")).strip()
        try:
            bins_per_hour = int(bins_per_hour_raw)
        except ValueError:
            return PipelinePacket.inactive(reason="Bins per hour must be an integer")

        if not 1 <= bins_per_hour <= 60:
            return PipelinePacket.inactive(reason="Bins per hour must be between 1 and 60")

        columns = ["Animal", "DateTime", variable.name]
        df = datatable.get_filtered_df(columns)

        result = get_actogram_result(
            datatable.dataset,
            df,
            variable,
            bins_per_hour,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
