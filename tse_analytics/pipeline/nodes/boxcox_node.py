from scipy.stats import boxcox

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class BoxCoxNode(PipelineNode):
    __identifier__ = "transformation"
    NODE_NAME = "Box-Cox"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("datatable")

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        selected_variable = packet.meta.get("selected_variable")
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")
        if selected_variable is None:
            return PipelinePacket.inactive(reason="No variable selected")

        datatable = datatable.clone()
        data = datatable.active_df[selected_variable].to_numpy()
        transformed_data, lambda_opt = boxcox(data)
        datatable.active_df[selected_variable] = transformed_data

        tooltip = f"<b>Result</b><br/>Lambda: {lambda_opt:.5f}"
        self.view.setToolTip(tooltip)

        return PipelinePacket(datatable, meta={"lambda": lambda_opt})
