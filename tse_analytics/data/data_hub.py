from typing import Optional
import gc
import pathlib

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache
from pyqtgraph import BusyCursor
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.dataset_component import DatasetComponent
from tse_datatools.data.group import Group

from tse_analytics.core.decorators import catch_error
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.messaging.messages import DatasetComponentChangedMessage, \
    DatasetImportedMessage, DatasetLoadedMessage, DatasetUnloadedMessage, DatasetRemovedMessage, \
    SelectedAnimalsChangedMessage, AnimalDataChangedMessage, DatasetChangedMessage, SelectedGroupsChangedMessage
from tse_analytics.models.workspace_model import WorkspaceModel


class DataHub(MessengerListener):
    def __init__(self, messenger: Messenger):
        MessengerListener.__init__(self)

        self.messenger = messenger
        self.register_to_messenger(self.messenger)

        self.workspace_model = WorkspaceModel()

        self.selected_dataset: Optional[Dataset] = None
        self.selected_dataset_component: Optional[DatasetComponent] = None

        self.selected_animals: list[Animal] = []
        self.selected_groups: list[Group] = []

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, DatasetComponentChangedMessage, self._on_dataset_component_changed)
        messenger.subscribe(self, SelectedAnimalsChangedMessage, self._on_selected_animals_changed)
        messenger.subscribe(self, SelectedGroupsChangedMessage, self._on_selected_groups_changed)

    def clear(self):
        self.selected_dataset = None
        self.selected_dataset_component = None
        self.selected_animals.clear()
        self.selected_groups.clear()
        QPixmapCache.clear()
        gc.collect()

    def broadcast_animal_data_changed(self):
        if len(self.selected_animals) > 0:
            self.messenger.broadcast(AnimalDataChangedMessage(self, self.selected_animals))

    def _on_dataset_changed(self, message: DatasetChangedMessage) -> None:
        if self.selected_dataset is message.data:
            return
        self.selected_dataset = message.data
        self.broadcast_animal_data_changed()

    def _on_dataset_component_changed(self, message: DatasetComponentChangedMessage) -> None:
        if self.selected_dataset_component is message.data:
            return
        self.selected_dataset_component = message.data
        self.broadcast_animal_data_changed()

    def _on_selected_animals_changed(self, message: SelectedAnimalsChangedMessage) -> None:
        self.selected_animals = message.animals
        self.broadcast_animal_data_changed()

    def _on_selected_groups_changed(self, message: SelectedGroupsChangedMessage) -> None:
        self.selected_groups = message.groups

    def load_workspace(self, path: str) -> None:
        with BusyCursor():
            self.clear()
            self.workspace_model.load_workspace(path)

    def save_workspace(self, path: str) -> None:
        with BusyCursor():
            self.workspace_model.save_workspace(path)

    def export_to_excel(self, path: str) -> None:
        with BusyCursor():
            self.workspace_model.export_to_excel(path)

    @catch_error("Could not import dataset")
    def import_dataset(self, path: str) -> None:
        with BusyCursor():
            name = pathlib.PurePath(path).name
            dataset = Dataset(name, path)
            self.workspace_model.add_dataset(dataset)
            self.messenger.broadcast(DatasetImportedMessage(self))

    @catch_error("Could not load dataset")
    def load_dataset(self, indexes: [QModelIndex]) -> None:
        with BusyCursor():
            self.workspace_model.load_dataset(indexes)
            self.messenger.broadcast(DatasetLoadedMessage(self))

    @catch_error("Could not close dataset")
    def close_dataset(self, indexes: [QModelIndex]) -> None:
        with BusyCursor():
            self.workspace_model.close_dataset(indexes)
            self.messenger.broadcast(DatasetUnloadedMessage(self))
            self.clear()

    @catch_error("Could not remove dataset")
    def remove_dataset(self, indexes: [QModelIndex]) -> None:
        self.workspace_model.remove_dataset(indexes)
        self.messenger.broadcast(DatasetRemovedMessage(self))
        self.clear()
