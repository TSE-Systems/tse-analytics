from typing import Optional
import gc

import pandas as pd
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache

from tse_analytics.core.view_mode import ViewMode
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.group import Group

from tse_analytics.core.decorators import catch_error
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.messaging.messages import (
    WorkspaceLoadedMessage,
    DatasetRemovedMessage,
    SelectedAnimalsChangedMessage,
    AnimalDataChangedMessage,
    DatasetChangedMessage,
    SelectedGroupsChangedMessage,
    GroupDataChangedMessage
)


class DataHub(MessengerListener):
    def __init__(self, messenger: Messenger):
        MessengerListener.__init__(self)

        self.messenger = messenger
        self.register_to_messenger(self.messenger)

        self.selected_dataset: Optional[Dataset] = None
        self.selected_animals: list[Animal] = []
        self.selected_groups: list[Group] = []

        self.view_mode = ViewMode.ANIMALS
        self.binning_params = BinningParams(pd.Timedelta('1H'), 'mean')

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, WorkspaceLoadedMessage, self._on_workspace_loaded)
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, SelectedAnimalsChangedMessage, self._on_selected_animals_changed)
        messenger.subscribe(self, SelectedGroupsChangedMessage, self._on_selected_groups_changed)

    def clear(self):
        self.selected_dataset = None
        self.selected_animals.clear()
        self.selected_groups.clear()
        QPixmapCache.clear()
        gc.collect()

    def _on_workspace_loaded(self, message: WorkspaceLoadedMessage) -> None:
        self.clear()
        self._broadcast_animal_data_changed()

    def _on_dataset_changed(self, message: DatasetChangedMessage) -> None:
        if self.selected_dataset is message.data:
            return
        self.selected_dataset = message.data
        self.selected_animals.clear()
        self.selected_groups.clear()
        self._broadcast_animal_data_changed()

    def _on_dataset_removed(self, message: DatasetRemovedMessage) -> None:
        self.clear()
        self._broadcast_animal_data_changed()

    def _on_selected_animals_changed(self, message: SelectedAnimalsChangedMessage) -> None:
        self.selected_animals = message.animals
        self._broadcast_animal_data_changed()

    def _on_selected_groups_changed(self, message: SelectedGroupsChangedMessage) -> None:
        self.selected_groups = message.groups
        self._broadcast_group_data_changed()

    def _broadcast_animal_data_changed(self):
        self.messenger.broadcast(AnimalDataChangedMessage(self, self.selected_animals))

    def _broadcast_group_data_changed(self):
        self.messenger.broadcast(GroupDataChangedMessage(self, self.selected_groups))

    @catch_error("Could not adjust dataset time")
    def adjust_dataset_time(self, indexes: [QModelIndex], delta: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.adjust_time(delta)
            self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def export_to_excel(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.export_to_excel(path)
