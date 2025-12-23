from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.pipeline.pipeline_node import PipelineNode


class ReportNode(PipelineNode):
    __identifier__ = "output"
    NODE_NAME = "Report"

    def __init__(self):
        super().__init__()
        self.add_input("input")

        self.add_text_input(
            "report_name",
            "Name",
            "Report",
            "Report name",
            "Report name",
        )

    def process(self, input):
        if input is None:
            return None

        report_content = None
        if isinstance(input, Datatable):
            report_content = input.active_df.to_html()
        elif isinstance(input, str):
            report_content = input

        if report_content is not None:
            name = str(self.get_property("report_name"))
            manager.add_report(
                Report(
                    manager.get_selected_dataset(),
                    name,
                    report_content,
                )
            )
