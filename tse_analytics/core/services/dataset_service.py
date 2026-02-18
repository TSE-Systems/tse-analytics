"""
Dataset service for TSE Analytics.

Manages dataset, datatable, and report CRUD operations, including
merging and cloning datasets.
"""

import copy
from uuid import uuid4

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService
from tse_analytics.modules.intellicage.data import intellicage_dataset_merger
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.phenomaster.data import phenomaster_dataset_merger
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


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
        first_dataset = datasets[0]
        merged_dataset = None
        if isinstance(first_dataset, PhenoMasterDataset):
            merged_dataset = phenomaster_dataset_merger.merge_datasets(
                new_dataset_name,
                datasets,
                single_run,
                continuous_mode,
                generate_new_animal_names,
            )
        elif isinstance(first_dataset, IntelliCageDataset):
            merged_dataset = intellicage_dataset_merger.merge_datasets(
                new_dataset_name,
                datasets,
                single_run,
                continuous_mode,
                generate_new_animal_names,
            )

        if merged_dataset is not None:
            self.add_dataset(merged_dataset)

    def clone_dataset(self, original_dataset: Dataset, new_dataset_name: str) -> None:
        """Create a deep copy of a dataset with a new name and add it to the workspace.

        Args:
            original_dataset: The dataset to clone.
            new_dataset_name: The name for the new cloned dataset.
        """
        new_dataset = copy.deepcopy(original_dataset)
        new_dataset.id = uuid4()
        new_dataset.metadata["name"] = new_dataset_name
        if new_dataset is not None:
            self.add_dataset(new_dataset)

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
