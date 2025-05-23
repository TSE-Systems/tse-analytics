import copy
import gc
import pickle
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QTimer

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.settings_manager import get_csv_import_settings
from tse_analytics.modules.intellicage.data import intellicage_dataset_merger
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.phenomaster.data import phenomaster_dataset_merger
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import load_csv_dataset
from tse_analytics.modules.phenomaster.submodules.actimot.io.data_loader import import_actimot_csv_data
from tse_analytics.modules.phenomaster.submodules.calo.io.data_loader import import_calo_csv_data
from tse_analytics.modules.phenomaster.submodules.drinkfeed.io.data_loader import import_drinkfeed_csv_data
from tse_analytics.modules.phenomaster.submodules.trafficage.io.data_loader import import_trafficage_csv_data


class Manager:
    def __init__(self):
        self._workspace = Workspace("Default Workspace")
        self._selected_dataset: Dataset | None = None
        self._selected_datatable: Datatable | None = None

    def get_workspace(self) -> Workspace:
        return self._workspace

    def get_selected_dataset(self):
        return self._selected_dataset

    def set_selected_dataset(self, dataset: Dataset | None):
        self._selected_dataset = dataset
        # self.set_selected_datatable(None)
        messaging.broadcast(messaging.DatasetChangedMessage(self, dataset))

    def get_selected_datatable(self):
        return self._selected_datatable

    def set_selected_datatable(self, datatable: Datatable | None):
        self._selected_datatable = datatable
        messaging.broadcast(messaging.DatatableChangedMessage(self, datatable))

    def new_workspace(self) -> None:
        self._workspace = Workspace("Workspace")
        self._cleanup_workspace()

    def load_workspace(self, path: str) -> None:
        with open(path, "rb") as file:
            self._workspace = pickle.load(file)
        self._cleanup_workspace()

    def save_workspace(self, path: str) -> None:
        with open(path, "wb") as file:
            pickle.dump(self._workspace, file)

    def import_csv_dataset(self, path: Path) -> None:
        dataset = load_csv_dataset(path, get_csv_import_settings())
        if dataset is not None:
            self.add_dataset(dataset)

    def import_drinkfeed_data(self, path: str) -> None:
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_drinkfeed_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.drinkfeed_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_actimot_data(self, path: str) -> None:
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_actimot_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.actimot_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_calo_data(self, path: str) -> None:
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_calo_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.calo_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def import_trafficage_data(self, path: str) -> None:
        dataset = self.get_selected_dataset()
        if dataset is not None and isinstance(dataset, PhenoMasterDataset):
            data = import_trafficage_csv_data(path, dataset, get_csv_import_settings())
            if data is not None:
                dataset.trafficage_data = data
                messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def add_datatable(self, datatable: Datatable) -> None:
        # TODO: careful here!
        datatable.dataset.add_datatable(datatable)
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def remove_datatable(self, datatable: Datatable) -> None:
        datatable.dataset.remove_datatable(datatable)
        self.set_selected_datatable(None)
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def add_dataset(self, dataset: Dataset) -> None:
        self._workspace.datasets[dataset.id] = dataset
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))

    def remove_dataset(self, dataset: Dataset) -> None:
        self._workspace.datasets.pop(dataset.id)
        self._cleanup_workspace()

    def _cleanup_workspace(self):
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
        new_dataset = copy.deepcopy(original_dataset)
        new_dataset.id = uuid4()
        new_dataset.metadata["name"] = new_dataset_name
        if new_dataset is not None:
            self.add_dataset(new_dataset)


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
import_trafficage_data = _instance.import_trafficage_data
add_dataset = _instance.add_dataset
remove_dataset = _instance.remove_dataset
add_datatable = _instance.add_datatable
remove_datatable = _instance.remove_datatable
merge_datasets = _instance.merge_datasets
clone_dataset = _instance.clone_dataset
