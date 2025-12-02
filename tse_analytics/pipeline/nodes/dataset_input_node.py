from NodeGraphQt import BaseNode
from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core import manager


class DatasetInputNode(BaseNode):
    """Node for selecting a dataset."""

    __identifier__ = "pipeline.input"
    NODE_NAME = "Dataset Input"

    def __init__(self):
        super().__init__()

        self.add_output("dataset")

        self.add_combo_menu(
            "dataset_name",
            "Datasets",
            items=[],
            tooltip="Please select a dataset",
        )
        self.initialize()

    def initialize(self):
        dataset_names = (
            [dataset.name for dataset in manager.get_workspace().datasets.values()]
            if len(manager.get_workspace().datasets) > 0
            else (["No datasets"])
        )
        widget: NodeComboBox = self.get_widget("dataset_name")
        widget.clear()
        widget.add_items(dataset_names)

        print(f"'{self.NODE_NAME}' node initialized")

    def process(self, context=None):
        dataset = self.get_dataset()
        print(f"'{self.NODE_NAME}' node processed")

    def get_dataset(self):
        """Get the selected dataset."""
        dataset_name = self.get_property("dataset_name")
        datasets = manager.get_workspace().datasets.values()
        for ds in datasets:
            if ds.name == dataset_name:
                return ds
        return None
