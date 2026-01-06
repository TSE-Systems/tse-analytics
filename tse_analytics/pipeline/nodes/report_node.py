from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class ReportNode(PipelineNode):
    __identifier__ = "output"
    NODE_NAME = "Report"

    def __init__(self):
        super().__init__()
        self.add_input("input")

        self.add_text_input(
            "report_name",
            "",
            "Report",
            "Report name",
            "Report name",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        value = packet.value
        if value is None:
            return PipelinePacket.inactive(reason="Invalid input")

        report_content = None
        if isinstance(value, Datatable):
            report_content = value.active_df.to_html()
        elif isinstance(value, str):
            report_content = value

        if report_content is not None:
            name = str(self.get_property("report_name"))
            manager.add_report(
                Report(
                    manager.get_selected_dataset(),
                    name,
                    report_content,
                )
            )

        return packet
