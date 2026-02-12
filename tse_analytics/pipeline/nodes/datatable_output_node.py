from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class DatatableOutputNode(PipelineNode):
    __identifier__ = "output"
    NODE_NAME = "Datatable Output"

    def __init__(self):
        super().__init__()
        self.add_input("input")

        self.add_text_input(
            "table_name",
            "",
            "Table",
            "Table name",
            "Table name",
        )

    def process(self, packet: PipelinePacket) -> None:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return

        datatable.name = str(self.get_property("table_name"))
        manager.add_datatable(datatable)
