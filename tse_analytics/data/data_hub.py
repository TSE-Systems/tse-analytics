import gc
from typing import Optional

import pandas as pd
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache

from tse_analytics.messaging.messages import (
    ClearDataMessage,
    DataChangedMessage,
    DatasetChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.processor import calculate_grouped_data
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.group import Group
from tse_datatools.data.variable import Variable


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Optional[Dataset] = None
        self.selected_animals: list[Animal] = []
        self.selected_groups: list[Group] = []
        self.selected_variables: list[Variable] = []

        self.grouping_mode = GroupingMode.ANIMALS
        self.apply_binning = False
        self.binning_params = BinningParams(pd.Timedelta("1H"), BinningOperation.MEAN)

        self.selected_variable = ""

    def clear(self):
        self.selected_dataset = None
        # self.apply_binning = False
        self.selected_animals.clear()
        self.selected_groups.clear()
        self.selected_variables.clear()
        QPixmapCache.clear()
        gc.collect()

        self.messenger.broadcast(ClearDataMessage(self))

    def set_grouping_mode(self, mode: GroupingMode):
        self.grouping_mode = mode
        self.messenger.broadcast(GroupingModeChangedMessage(self, self.grouping_mode))

    def set_selected_dataset(self, dataset: Dataset) -> None:
        if self.selected_dataset is dataset:
            return
        self.selected_dataset = dataset
        self.selected_animals.clear()
        self.selected_groups.clear()
        self.selected_variables.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self, animals: list[Animal]) -> None:
        self.selected_animals = animals
        self._broadcast_data_changed()

    def set_selected_groups(self, groups: list[Group]) -> None:
        self.selected_groups = groups
        self._broadcast_data_changed()

    def set_selected_variables(self, variables: list[Variable]) -> None:
        self.selected_variables = variables
        self._broadcast_data_changed()

    def _broadcast_data_changed(self):
        self.messenger.broadcast(DataChangedMessage(self))

    def adjust_dataset_time(self, indexes: list[QModelIndex], delta: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.adjust_time(delta)
            self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def export_to_excel(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.export_to_excel(path)

    def get_current_df(self) -> pd.DataFrame:
        result = self.selected_dataset.original_df.copy()

        timedelta = self.selected_dataset.sampling_interval if not self.apply_binning else self.binning_params.timedelta

        if self.grouping_mode == GroupingMode.GROUPS and len(self.selected_dataset.groups) > 0:
            result = calculate_grouped_data(
                result, timedelta, self.binning_params.operation, self.grouping_mode, self.selected_variable
            )
            if len(self.selected_groups) > 0:
                group_ids = [group.name for group in self.selected_groups]
                result = result[result["Group"].isin(group_ids)]
            # TODO: should or should not?
            # result = result.dropna()
        elif self.grouping_mode == GroupingMode.ANIMALS and len(self.selected_dataset.animals) > 0:
            if len(self.selected_animals) > 0:
                animal_ids = [animal.id for animal in self.selected_animals]
                result = result[result["Animal"].isin(animal_ids)]
                if self.apply_binning:
                    result = calculate_grouped_data(
                        result, timedelta, self.binning_params.operation, self.grouping_mode, self.selected_variable
                    )
        if self.grouping_mode == GroupingMode.RUNS:
            result = calculate_grouped_data(
                result, timedelta, self.binning_params.operation, self.grouping_mode, self.selected_variable
            )
            # TODO: should or should not?
            # result = result.dropna()

        return result
