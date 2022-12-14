from PySide6.QtCore import QModelIndex

from tse_analytics.models.workspace_model import WorkspaceModel
from tse_datatools.data.dataset import Dataset


class WorkspaceManager:
    def __init__(self):
        self.workspace_model = WorkspaceModel()

    def load_workspace(self, path: str) -> None:
        self.workspace_model.load_workspace(path)

    def save_workspace(self, path: str) -> None:
        self.workspace_model.save_workspace(path)

    def add_dataset(self, dataset: Dataset) -> None:
        self.workspace_model.add_dataset(dataset)

    def remove_dataset(self, indexes: list[QModelIndex]) -> None:
        self.workspace_model.remove_dataset(indexes)
