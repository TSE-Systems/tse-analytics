from loguru import logger
from PySide6.QtCore import QModelIndex, QThreadPool
from PySide6.QtWidgets import QWidget
from tse_analytics.data.dataset import Dataset

from tse_analytics.core.licensing import LicenseManager
from tse_analytics.data.data_hub import DataHub
from tse_analytics.helpers.dataset_merger import merge_datasets
from tse_analytics.loaders.dataset_loader import DatasetLoader
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.models.workspace_model import WorkspaceModel


class Manager:
    messenger = Messenger()
    workspace = WorkspaceModel()
    data = DataHub(messenger)
    threadpool = QThreadPool()

    def __init__(self):
        # logging.info(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")
        logger.info(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")
        LicenseManager.load_license()

    @classmethod
    def load_workspace(cls, path: str) -> None:
        cls.workspace.load_workspace(path)
        cls.data.clear()

    @classmethod
    def save_workspace(cls, path: str) -> None:
        cls.workspace.save_workspace(path)

    @classmethod
    def import_dataset(cls, path: str) -> None:
        dataset = DatasetLoader.load(path)
        if dataset is not None:
            cls.workspace.add_dataset(dataset)

    @classmethod
    def import_calo_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace.add_calo_details(dataset_index, path)

    @classmethod
    def remove_dataset(cls, indexes: list[QModelIndex]) -> None:
        cls.workspace.remove_dataset(indexes)
        cls.data.clear()

    @classmethod
    def merge_datasets(
        cls, new_dataset_name: str, datasets: list[Dataset], single_run: bool, parent_widget: QWidget
    ) -> None:
        result_dataset = merge_datasets(new_dataset_name, datasets, single_run, parent_widget)
        if result_dataset is not None:
            cls.workspace.add_dataset(result_dataset)
