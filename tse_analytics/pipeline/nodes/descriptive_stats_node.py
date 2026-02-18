from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_great_table
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class DescriptiveStatsNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Descriptive Statistics"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        descriptive_df = datatable.active_df.describe().T.reset_index()
        report = get_great_table(
            descriptive_df,
            "Descriptive Statistics",
            decimals=3,
            rowname_col="index",
        ).as_raw_html(inline_css=True)

        return PipelinePacket(datatable, report=report)
