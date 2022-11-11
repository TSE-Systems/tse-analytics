from PySide6.QtCore import QModelIndex

from tse_analytics.core.decorators import catch_error
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messages import DatasetImportedMessage, WorkspaceLoadedMessage, DatasetRemovedMessage
from tse_analytics.models.workspace_model import WorkspaceModel
from tse_datatools.loaders.dataset_loader import DatasetLoader


class WorkspaceManager:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger
        self.workspace_model = WorkspaceModel()

    def load_workspace(self, path: str) -> None:
        self.workspace_model.load_workspace(path)
        self.messenger.broadcast(WorkspaceLoadedMessage(self))

    def save_workspace(self, path: str) -> None:
        self.workspace_model.save_workspace(path)

    @catch_error("Could not import dataset")
    def import_dataset(self, path: str) -> None:
        dataset = DatasetLoader.load(path)
        self.workspace_model.add_dataset(dataset)
        self.messenger.broadcast(DatasetImportedMessage(self, dataset))

    def remove_dataset(self, indexes: [QModelIndex]) -> None:
        self.workspace_model.remove_dataset(indexes)
        self.messenger.broadcast(DatasetRemovedMessage(self))
