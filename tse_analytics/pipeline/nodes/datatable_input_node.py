from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class DatatableInputNode(PipelineNode):
    """Node for selecting a datatable."""

    __identifier__ = "input"
    NODE_NAME = "Datatable"

    def __init__(self):
        super().__init__()

        self.add_output("datatable")

        dataset = manager.get_selected_dataset()
        datatable_names = (
            [datatable.name for datatable in dataset.datatables.values()]
            if len(dataset.datatables) > 0
            else ["No datatables"]
        )

        self.add_combo_menu(
            "datatable_name",
            "",
            items=datatable_names,
            tooltip="Please select a datatable",
        )

    def initialize(self, dataset: Dataset, datatable: Datatable):
        pass

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable_name = self.get_property("datatable_name")
        if datatable_name in manager.get_selected_dataset().datatables:
            datatable = manager.get_selected_dataset().datatables[datatable_name]
            return PipelinePacket(datatable)
        return PipelinePacket.inactive(reason="Datatable not found")
