from typing import Optional
import gc

import pandas as pd
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache

from tse_analytics.core.view_mode import ViewMode
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.processor import calculate_grouped_data
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.group import Group

from tse_analytics.core.decorators import catch_error
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messages import (
    ClearDataMessage,
    AnimalDataChangedMessage,
    DatasetChangedMessage,
    GroupDataChangedMessage
)


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Optional[Dataset] = None
        self.selected_animals: list[Animal] = []
        self.selected_groups: list[Group] = []

        self.view_mode = ViewMode.ANIMALS
        self.apply_binning = False
        self.binning_params = BinningParams(pd.Timedelta('1H'), 'mean')

    def clear(self):
        self.selected_dataset = None
        # self.apply_binning = False
        self.selected_animals.clear()
        self.selected_groups.clear()
        QPixmapCache.clear()
        gc.collect()

        self.messenger.broadcast(ClearDataMessage(self))

    def set_view_mode(self, mode: ViewMode):
        self.view_mode = mode

    def set_selected_dataset(self, dataset: Dataset) -> None:
        if self.selected_dataset is dataset:
            return
        self.selected_dataset = dataset
        self.selected_animals.clear()
        self.selected_groups.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self, animals: list[Animal]) -> None:
        self.selected_animals = animals
        self._broadcast_animal_data_changed()

    def set_selected_groups(self, groups: list[Group]) -> None:
        self.selected_groups = groups
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

    def get_current_df(self) -> pd.DataFrame:
        result = self.selected_dataset.original_df.copy()

        timedelta = self.selected_dataset.sampling_interval if not self.apply_binning else self.binning_params.timedelta

        if self.view_mode == ViewMode.GROUPS and len(self.selected_dataset.groups) > 0:
            result = calculate_grouped_data(result, timedelta, self.binning_params.operation, self.view_mode)
            if len(self.selected_groups) > 0:
                group_ids = [group.name for group in self.selected_groups]
                result = result[result['Group'].isin(group_ids)]
            # TODO: should or should not?
            # result = result.dropna()
        elif self.view_mode == ViewMode.ANIMALS and len(self.selected_dataset.animals) > 0:
            if len(self.selected_animals) > 0:
                animal_ids = [animal.id for animal in self.selected_animals]
                result = result[result['Animal'].isin(animal_ids)]
                if self.apply_binning:
                    result = calculate_grouped_data(result, timedelta, self.binning_params.operation, self.view_mode)
        return result
