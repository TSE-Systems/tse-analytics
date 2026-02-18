"""
Import service for TSE Analytics.

Orchestrates data import from CSV, DrinkFeed, ActiMot, Calo,
and GroupHousing sources.
"""

from pathlib import Path

from tse_analytics.core import messaging
from tse_analytics.core.services.dataset_service import DatasetService
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService
from tse_analytics.core.settings_manager import get_csv_import_settings
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import load_csv_dataset
from tse_analytics.modules.phenomaster.submodules.actimot.io.data_loader import import_actimot_csv_data
from tse_analytics.modules.phenomaster.submodules.calo.io.data_loader import import_calo_csv_data
from tse_analytics.modules.phenomaster.submodules.drinkfeed.io.data_loader import import_drinkfeed_bin_csv_data
from tse_analytics.modules.phenomaster.submodules.grouphousing.io.data_loader import import_grouphousing_csv_data


class ImportService:
    """Orchestrates data import from various sources.

    Handles CSV dataset import as well as submodule-specific imports
    (DrinkFeed, ActiMot, Calo, GroupHousing) into PhenoMaster datasets.
    """

    def __init__(self, selection: SelectionService, dataset: DatasetService, workspace: WorkspaceService):
        self._selection = selection
        self._dataset = dataset
        self._workspace = workspace

    def import_csv_dataset(self, path: Path) -> None:
        """Import a CSV dataset and add it to the workspace.

        Args:
            path: The path to the CSV file to import.
        """
        dataset = load_csv_dataset(path, get_csv_import_settings())
        if dataset is not None:
            self._dataset.add_dataset(dataset)

    def import_drinkfeed_data(self, path: str) -> None:
        """Import DrinkFeed data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the DrinkFeed CSV file to import.
        """
        dataset = self._selection.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_drinkfeed_bin_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.drinkfeed_bin_data = data
                ws = self._workspace.get_workspace()
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def import_actimot_data(self, path: str) -> None:
        """Import ActiMot data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the ActiMot CSV file to import.
        """
        dataset = self._selection.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_actimot_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.actimot_data = data
                ws = self._workspace.get_workspace()
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def import_calo_data(self, path: str) -> None:
        """Import Calorimetry data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the Calorimetry CSV file to import.
        """
        dataset = self._selection.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_calo_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.calo_data = data
                ws = self._workspace.get_workspace()
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))

    def import_grouphousing_data(self, path: str) -> None:
        """Import group housing data into the currently selected PhenoMaster dataset.

        Args:
            path: The path to the group housing CSV file to import.
        """
        dataset = self._selection.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_grouphousing_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.grouphousing_data = data
                ws = self._workspace.get_workspace()
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, ws))
