"""Base nodes for pipeline editor."""

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum
from PySide6.QtWidgets import QComboBox

from tse_analytics.core import manager


class DatasetOutputNode(BaseNode):
    """Node for outputting processed dataset."""

    __identifier__ = "pipeline.output"
    NODE_NAME = "Dataset Output"

    def __init__(self):
        super().__init__()
        self.add_input("dataset", color=(180, 80, 80))
        self.create_property("output_name", "processed_data")

    def set_dataset(self, dataset):
        """Set the output dataset."""
        self._output_dataset = dataset

    def get_dataset(self):
        """Get the output dataset."""
        return getattr(self, "_output_dataset", None)


class ViewerNode(BaseNode):
    """Node for visualizing data at any pipeline stage."""

    __identifier__ = "pipeline.viewer"
    NODE_NAME = "Data Viewer"

    def __init__(self):
        super().__init__()
        self.add_input("dataset", color=(180, 80, 80))
        self.add_output("dataset", color=(180, 80, 80))
        self.create_property("auto_view", True)

    def view_data(self, dataset):
        """Display the data (to be connected to a viewer widget)."""
        # This will be implemented when we add the viewer functionality
        if dataset is not None:
            print(f"Viewing dataset: {dataset}")
