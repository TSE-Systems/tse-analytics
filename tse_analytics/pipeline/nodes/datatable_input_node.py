from NodeGraphQt import BaseNode
from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core import manager


class DatatableInputNode(BaseNode):
    """Node for selecting a datatable."""

    __identifier__ = "pipeline.input"
    NODE_NAME = "Datatable Input"

    def __init__(self):
        super().__init__()

        self.add_output("datatable")

        self.add_combo_menu(
            "datatable_name",
            "Datatable",
            items=[],
            tooltip="Please select a datatable",
        )
        self.initialize()

    def initialize(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            datatable_names = ["No datatables"]
        else:
            datatable_names = (
                [datatable.name for datatable in dataset.datatables.values()]
                if len(dataset.datatables) > 0
                else (["No datatables"])
            )
        widget: NodeComboBox = self.get_widget("datatable_name")
        widget.clear()
        widget.add_items(datatable_names)

        print(f"'{self.NODE_NAME}' node initialized")

    def process(self, context=None):
        datatable = self.get_datatable()
        return datatable

    def get_datatable(self):
        """Get the selected datatable."""
        datatable_name = self.get_property("datatable_name")
        if datatable_name in manager.get_selected_dataset().datatables:
            return manager.get_selected_dataset().datatables[datatable_name]
        return None
