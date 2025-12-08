"""
Core manager module for TSE Analytics.

This module provides a singleton Manager class that serves as the central point
for managing workspaces, datasets, and datatables in the application. It handles
operations such as creating, loading, and saving workspaces, importing data from
various sources, and managing the selection state of datasets and datatables.
"""

import copy
import gc
import pickle
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QTimer

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.settings_manager import get_csv_import_settings
from tse_analytics.modules.intellicage.data import intellicage_dataset_merger
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.phenomaster.data import phenomaster_dataset_merger
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import load_csv_dataset
from tse_analytics.modules.phenomaster.submodules.actimot.io.data_loader import import_actimot_csv_data
from tse_analytics.modules.phenomaster.submodules.calo.io.data_loader import import_calo_csv_data
from tse_analytics.modules.phenomaster.submodules.drinkfeed.io.data_loader import import_drinkfeed_bin_csv_data
from tse_analytics.modules.phenomaster.submodules.grouphousing.io.data_loader import import_grouphousing_csv_data


class Manager:
    """
    Central manager class for TSE Analytics application.

    This class serves as the central point for managing workspaces, datasets, and
    datatables in the application. It maintains the current workspace and selection
    state, and provides methods for various operations such as creating, loading,
    and saving workspaces, importing data from various sources, and managing datasets
    and datatables.

    This class is implemented as a singleton, with its instance methods exposed as
    module-level functions for easy access throughout the application.
    """

    def __init__(self):
        """
        Initialize the Manager with a default workspace and empty selections.
        """
        self._workspace = Workspace("Default Workspace")
        self._selected_dataset: Dataset | None = None
        self._selected_datatable: Datatable | None = None

    def get_workspace(self) -> Workspace:
        """
        Get the current workspace.

        Returns:
            The current workspace object.
        """
        return self._workspace

    def get_selected_dataset(self):
        """
        Get the currently selected dataset.

        Returns:
            The currently selected dataset, or None if no dataset is selected.
        """
        return self._selected_dataset

    def set_selected_dataset(self, dataset: Dataset | None):
        """
        Set the currently selected dataset and broadcast a change message.

        Args:
            dataset: The dataset to select, or None to clear the selection.
        """
        self._selected_dataset = dataset
        # self.set_selected_datatable(None)
        messaging.broadcast(messaging.DatasetChangedMessage(self, dataset))

    def get_selected_datatable(self):
        """
        Get the currently selected datatable.

        Returns:
            The currently selected datatable, or None if no datatable is selected.
        """
        return self._selected_datatable

    def set_selected_datatable(self, datatable: Datatable | None):
        """
        Set the currently selected datatable and broadcast a change message.

        Args:
            datatable: The datatable to select, or None to clear the selection.
        """
        self._selected_datatable = datatable
        messaging.broadcast(messaging.DatatableChangedMessage(self, datatable))

    def new_workspace(self) -> None:
        """
        Create a new empty workspace and clear selections.
        """
        self._workspace = Workspace("Workspace")
        self._cleanup_workspace()

    def load_workspace(self, path: str) -> None:
        """
        Load a workspace from a file and clear selections.

        Args:
            path: The path to the workspace file to load.
        """
        with open(path, "rb") as file:
            self._workspace = pickle.load(file)
        self._cleanup_workspace()

    def save_workspace(self, path: str) -> None:
        """
        Save the current workspace to a file.

        Args:
            path: The path where the workspace file will be saved.
        """
        with open(path, "wb") as file:
            pickle.dump(self._workspace, file)

    def import_csv_dataset(self, path: Path) -> None:
        """
        Import a CSV dataset and add it to the workspace.

        Args:
            path: The path to the CSV file to import.
        """
        dataset = load_csv_dataset(path, get_csv_import_settings())
        if dataset is not None:
            self.add_dataset(dataset)

    def import_drinkfeed_data(self, path: str) -> None:
        """
        Import DrinkFeed data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the DrinkFeed CSV file to import.
        """
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_drinkfeed_bin_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.drinkfeed_bin_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_actimot_data(self, path: str) -> None:
        """
        Import ActiMot data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the ActiMot CSV file to import.
        """
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_actimot_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.actimot_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_calo_data(self, path: str) -> None:
        """
        Import Calorimetry data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the Calorimetry CSV file to import.
        """
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_calo_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.calo_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_grouphousing_data(self, path: str) -> None:
        """
        Import group housing data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the group housing CSV file to import.
        """
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_grouphousing_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.grouphousing_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def add_datatable(self, datatable: Datatable) -> None:
        """
        Add a datatable to its dataset and broadcast a workspace change message.

        Args:
            datatable: The datatable to add.
        """
        # TODO: careful here!
        datatable.dataset.add_datatable(datatable)
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def remove_datatable(self, datatable: Datatable) -> None:
        """
        Remove a datatable from its dataset, clear the selection if needed,
        and broadcast a workspace change message.

        Args:
            datatable: The datatable to remove.
        """
        datatable.dataset.remove_datatable(datatable)
        self.set_selected_datatable(None)
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def add_dataset(self, dataset: Dataset) -> None:
        """
        Add a dataset to the workspace and broadcast a workspace change message.

        Args:
            dataset: The dataset to add.
        """
        self._workspace.datasets[dataset.id] = dataset
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def remove_dataset(self, dataset: Dataset) -> None:
        """
        Remove a dataset from the workspace and clean up the workspace.

        Args:
            dataset: The dataset to remove.
        """
        self._workspace.datasets.pop(dataset.id)
        self._cleanup_workspace()

    def _cleanup_workspace(self):
        """
        Clean up the workspace by clearing selections and triggering garbage collection.

        This method is called after operations that significantly change the workspace,
        such as loading a new workspace or removing a dataset.
        """
        self.set_selected_datatable(None)
        self.set_selected_dataset(None)
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))
        QTimer.singleShot(1000, gc.collect)

    def merge_datasets(
        self,
        new_dataset_name: str,
        datasets: list[Dataset],
        single_run: bool,
        continuous_mode: bool,
        generate_new_animal_names: bool,
    ) -> None:
        """
        Merge multiple datasets into a new dataset and add it to the workspace.

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
        """
        Create a deep copy of a dataset with a new name and add it to the workspace.

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
        # TODO: careful here!
        report.dataset.add_report(report)
        messaging.broadcast(messaging.ReportsChangedMessage(self, report))

    def delete_report(self, report: Report) -> None:
        report.dataset.delete_report(report.name)
        messaging.broadcast(messaging.ReportsChangedMessage(self, report))


_instance = Manager()


get_workspace = _instance.get_workspace
get_selected_dataset = _instance.get_selected_dataset
set_selected_dataset = _instance.set_selected_dataset
get_selected_datatable = _instance.get_selected_datatable
set_selected_datatable = _instance.set_selected_datatable
new_workspace = _instance.new_workspace
load_workspace = _instance.load_workspace
save_workspace = _instance.save_workspace
import_csv_dataset = _instance.import_csv_dataset
import_drinkfeed_data = _instance.import_drinkfeed_data
import_actimot_data = _instance.import_actimot_data
import_calo_data = _instance.import_calo_data
import_grouphousing_data = _instance.import_grouphousing_data
add_dataset = _instance.add_dataset
remove_dataset = _instance.remove_dataset
add_datatable = _instance.add_datatable
remove_datatable = _instance.remove_datatable
merge_datasets = _instance.merge_datasets
clone_dataset = _instance.clone_dataset
add_report = _instance.add_report
delete_report = _instance.delete_report
