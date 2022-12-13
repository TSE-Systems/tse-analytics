from PySide6.QtCore import QModelIndex, QThreadPool

from tse_analytics.data.data_hub import DataHub
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.workspace.workspace_manager import WorkspaceManager
from tse_datatools.loaders.dataset_loader import DatasetLoader


class Manager:
    messenger = Messenger()
    workspace = WorkspaceManager()
    data = DataHub(messenger)
    threadpool = QThreadPool()

    def __init__(self):
        print(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")

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
    def remove_dataset(cls, indexes: [QModelIndex]) -> None:
        cls.workspace.remove_dataset(indexes)
        cls.data.clear()
