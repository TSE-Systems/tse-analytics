"""
Dataset service for TSE Analytics.

Manages dataset, datatable, and report CRUD operations, including
merging and cloning datasets.
"""

from uuid import uuid7

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService
from tse_analytics.core.utils import data_merger


class DatasetService:
    """Manages dataset, datatable, and report CRUD operations.

    Provides methods for adding, removing, merging, and cloning datasets,
    as well as managing datatables and reports within datasets.
    """

    def __init__(self, workspace: WorkspaceService, selection: SelectionService):
        self._workspace = workspace
        self._selection = selection

    def add_dataset(self, dataset: Dataset) -> None:
        """Add a dataset to the workspace and broadcast a workspace change message.

        Args:
            dataset: The dataset to add.
        """
        ws = self._workspace.get_workspace()
        ws.datasets[dataset.id] = dataset
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def remove_dataset(self, dataset: Dataset) -> None:
        """Remove a dataset from the workspace and clean up.

        Args:
            dataset: The dataset to remove.
        """
        ws = self._workspace.get_workspace()
        ws.datasets.pop(dataset.id)
        self._workspace._cleanup_workspace()

    def add_datatable(self, datatable: Datatable) -> None:
        """Add a datatable to its dataset and broadcast a workspace change message.

        Args:
            datatable: The datatable to add.
        """
        # TODO: careful here!
        datatable.dataset.add_datatable(datatable)
        ws = self._workspace.get_workspace()
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def remove_datatable(self, datatable: Datatable) -> None:
        """Remove a datatable from its dataset, clear the selection if needed,
        and broadcast a workspace change message.

        Args:
            datatable: The datatable to remove.
        """
        datatable.dataset.remove_datatable(datatable)
        self._selection.set_selected_datatable(None)
        ws = self._workspace.get_workspace()
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def merge_datasets(
        self,
        new_dataset_name: str,
        datasets: list[Dataset],
        single_run: bool,
        continuous_mode: bool,
        generate_new_animal_names: bool,
    ) -> None:
        """Merge multiple datasets into a new dataset and add it to the workspace.

        This method determines the type of the first dataset in the list and calls
        the appropriate merger function to create a new merged dataset.

        Args:
            new_dataset_name: The name for the new merged dataset.
            datasets: A list of datasets to merge.
            single_run: Whether to treat all datasets as a single run.
            continuous_mode: Whether to use continuous mode for merging.
            generate_new_animal_names: Whether to generate new animal names.
        """
        merged_dataset = data_merger.merge_datasets(
            new_dataset_name,
            datasets,
            single_run,
            continuous_mode,
            generate_new_animal_names,
        )

        if merged_dataset is not None:
            self.add_dataset(merged_dataset)

    def clone_dataset(self, original_dataset: Dataset, new_name: str) -> None:
        """Create a deep copy of a dataset with a new name and add it to the workspace.

        Args:
            original_dataset: The dataset to clone.
            new_name: The name for the new cloned dataset.
        """
        new_dataset = original_dataset.clone()
        new_dataset.name = new_name
        if new_dataset is not None:
            self.add_dataset(new_dataset)

    def clone_datatable(self, original_datatable: Datatable, new_name: str) -> None:
        """Create a deep copy of a datatable with a new name and add it to the workspace.

        Args:
            original_datatable: The datatable to clone.
            new_name: The name for the new cloned datatable.
        """
        new_datatable = original_datatable.clone()
        new_datatable.id = uuid7()
        new_datatable.name = new_name
        if new_datatable is not None:
            self.add_datatable(new_datatable)

    def clone_report(self, original_report: Report, new_name: str) -> None:
        """Create a deep copy of a report with a new name and add it to the workspace.

        Args:
            original_report: The report to clone.
            new_name: The name for the new cloned report.
        """
        new_report = original_report.clone()
        new_report.id = uuid7()
        new_report.name = new_name
        if new_report is not None:
            self.add_report(new_report)

    def add_report(self, report: Report) -> None:
        """Add a report to its parent dataset.

        Args:
            report: The report to add.
        """
        # TODO: careful here!
        report.dataset.add_report(report)
        messaging.broadcast(messaging.ReportsChangedMessage(self, report))

    def delete_report(self, report: Report) -> None:
        """Delete a report from its parent dataset.

        Args:
            report: The report to delete.
        """
        report.dataset.delete_report(report.name)
        messaging.broadcast(messaging.ReportsChangedMessage(self, report))
