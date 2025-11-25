"""Base nodes for pipeline editor."""

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum
from PySide6.QtWidgets import QComboBox

from tse_analytics.core import manager


class DatasetInputNode(BaseNode):
    """Node for selecting and inputting a dataset."""

    __identifier__ = "pipeline.input"
    NODE_NAME = "Dataset Input"

    def __init__(self):
        super().__init__()
        self.add_output("dataset", color=(180, 80, 80))
        # self.create_property("dataset_name", "", widget_type=QComboBox)

        # Populate with available datasets
        # self._update_dataset_list()

        items = [dataset.name for dataset in manager.get_workspace().datasets.values()]
        self.add_combo_menu("DatasetsName", "Datasets", items=items, tooltip="example custom tooltip")

    def _update_dataset_list(self):
        """Update the list of available datasets."""
        datasets = manager.get_workspace().datasets
        dataset_names = [ds.name for ds in datasets] if datasets else ["No datasets loaded"]

        # Update the property widget
        widget = self.get_property("dataset_name")
        if hasattr(widget, "clear"):
            widget.clear()
            widget.addItems(dataset_names)

    def get_dataset(self):
        """Get the selected dataset."""
        dataset_name = self.get_property("dataset_name")
        datasets = manager.get_workspace().datasets
        for ds in datasets:
            if ds.name == dataset_name:
                return ds
        return None


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
