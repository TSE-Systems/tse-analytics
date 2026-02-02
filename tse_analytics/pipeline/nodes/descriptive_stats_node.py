import numpy as np

from tse_analytics.core.data.datatable import Datatable
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

        report = (
            np
            .round(datatable.active_df.describe(), 3)
            .T[
                [
                    "count",
                    "mean",
                    "std",
                    "min",
                    "max",
                ]
            ]
            .to_html()
        )

        return PipelinePacket(datatable, report=report)
