from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_great_table
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

    def process(self, packet: PipelinePacket) -> None:
        report = None
        if packet.report is not None:
            report = packet.report
        else:
            value = packet.value
            if isinstance(value, Datatable):
                report = get_great_table(
                    value.df,
                    value.name,
                ).as_raw_html(inline_css=True)
            elif isinstance(value, str):
                report = value

        if report is not None:
            report_name = str(self.get_property("report_name"))
            manager.add_report(
                Report(
                    manager.get_selected_dataset(),
                    report_name,
                    report,
                )
            )
