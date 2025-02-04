import copy
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QModelIndex, QSettings

from tse_analytics.core import messaging
from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.models.workspace_model import WorkspaceModel
from tse_analytics.modules.phenomaster.data import pm_dataset_merger
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import load_csv_dataset


class Manager:
    def __init__(self):
        self._workspace_model = WorkspaceModel()
        self._selected_dataset: Dataset | None = None

    def get_workspace_model(self):
        return self._workspace_model

    def get_selected_dataset(self):
        return self._selected_dataset

    def set_selected_dataset(self, dataset: Dataset | None):
        self._selected_dataset = dataset
        messaging.broadcast(messaging.DatasetChangedMessage(self, dataset))

    def load_workspace(self, path: str) -> None:
        self.set_selected_dataset(None)
        self._workspace_model.load_workspace(path)

    def save_workspace(self, path: str) -> None:
        self._workspace_model.save_workspace(path)

    def import_csv_dataset(self, path: Path) -> None:
        settings = QSettings()
        csv_import_settings: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
        dataset = load_csv_dataset(path, csv_import_settings)
        if dataset is not None:
            self._workspace_model.add_dataset(dataset)

    def import_meal_details(self, dataset_index: QModelIndex, path: str) -> None:
        self._workspace_model.add_meal_details(dataset_index, path)

    def import_actimot_details(self, dataset_index: QModelIndex, path: str) -> None:
        self._workspace_model.add_actimot_details(dataset_index, path)

    def import_calo_details(self, dataset_index: QModelIndex, path: str) -> None:
        self._workspace_model.add_calo_details(dataset_index, path)

    def import_trafficage_data(self, dataset_index: QModelIndex, path: str) -> None:
        self._workspace_model.add_trafficage_data(dataset_index, path)

    def remove_dataset(self, indexes: list[QModelIndex]) -> None:
        self._workspace_model.remove_dataset(indexes)
        self.set_selected_dataset(None)

    def merge_datasets(
        self,
        new_dataset_name: str,
        datasets: list[Dataset],
        single_run: bool,
        continuous_mode: bool,
        generate_new_animal_names: bool,
    ) -> None:
        merged_dataset = pm_dataset_merger.merge_datasets(
            new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names
        )
        if merged_dataset is not None:
            self._workspace_model.add_dataset(merged_dataset)

    def clone_dataset(self, original_dataset: Dataset, new_dataset_name: str) -> None:
        new_dataset = copy.deepcopy(original_dataset)
        new_dataset.id = uuid4()
        new_dataset.name = new_dataset_name
        if new_dataset is not None:
            self._workspace_model.add_dataset(new_dataset)


_instance = Manager()

get_workspace_model = _instance.get_workspace_model
get_selected_dataset = _instance.get_selected_dataset
set_selected_dataset = _instance.set_selected_dataset
load_workspace = _instance.load_workspace
save_workspace = _instance.save_workspace
import_csv_dataset = _instance.import_csv_dataset
import_meal_details = _instance.import_meal_details
import_actimot_details = _instance.import_actimot_details
import_calo_details = _instance.import_calo_details
import_trafficage_data = _instance.import_trafficage_data
remove_dataset = _instance.remove_dataset
merge_datasets = _instance.merge_datasets
clone_dataset = _instance.clone_dataset
