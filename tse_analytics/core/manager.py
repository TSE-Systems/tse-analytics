import copy
import timeit
from pathlib import Path

from loguru import logger
from PySide6.QtCore import QModelIndex, QSettings, QThreadPool

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.data_hub import DataHub
from tse_analytics.core.dataset_merger import merge_datasets
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.models.workspace_model import WorkspaceModel
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import CsvDatasetLoader
from tse_analytics.modules.phenomaster.io.polars_dataset_loader import import_tse_dataset
from tse_analytics.modules.phenomaster.io.tse_dataset_loader import TseDatasetLoader


class Manager:
    messenger = Messenger()
    workspace = WorkspaceModel()
    data = DataHub(messenger)
    threadpool = QThreadPool()

    def __init__(self):
        # logging.info(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")
        logger.info(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")

    @classmethod
    def load_workspace(cls, path: str) -> None:
        cls.workspace.load_workspace(path)
        cls.data.clear()

    @classmethod
    def save_workspace(cls, path: str) -> None:
        cls.workspace.save_workspace(path)

    @classmethod
    def import_csv_dataset(cls, path: Path) -> None:
        settings = QSettings()
        csv_import_settings: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
        dataset = CsvDatasetLoader.load(path, csv_import_settings)
        if dataset is not None:
            cls.workspace.add_dataset(dataset)

    @classmethod
    def import_tse_dataset(cls, path: Path) -> None:
        tic = timeit.default_timer()
        # dataset = TseDatasetLoader.load(path)
        dataset = import_tse_dataset(path)
        print(f"Import complete: {timeit.default_timer() - tic} sec")
        if dataset is not None:
            cls.workspace.add_dataset(dataset)

    @classmethod
    def import_meal_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace.add_meal_details(dataset_index, path)

    @classmethod
    def import_actimot_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace.add_actimot_details(dataset_index, path)

    @classmethod
    def import_calo_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace.add_calo_details(dataset_index, path)

    @classmethod
    def remove_dataset(cls, indexes: list[QModelIndex]) -> None:
        cls.workspace.remove_dataset(indexes)
        cls.data.clear()

    @classmethod
    def merge_datasets(
        cls, new_dataset_name: str, datasets: list[Dataset], single_run: bool, continuous_mode: bool
    ) -> None:
        merged_dataset = merge_datasets(new_dataset_name, datasets, single_run, continuous_mode)
        if merged_dataset is not None:
            cls.workspace.add_dataset(merged_dataset)

    @classmethod
    def clone_dataset(cls, original_dataset: Dataset, new_dataset_name: str) -> None:
        new_dataset = copy.deepcopy(original_dataset)
        new_dataset.name = new_dataset_name
        if new_dataset is not None:
            cls.workspace.add_dataset(new_dataset)
