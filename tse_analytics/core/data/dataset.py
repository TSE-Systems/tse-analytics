from copy import deepcopy
from datetime import datetime
from uuid import uuid4

import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import Animal, Factor, FactorLevel
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem


class Dataset:
    def __init__(
        self,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        self.id = uuid4()
        self.metadata = metadata

        self.animals = animals
        self.factors: dict[str, Factor] = {}
        self.datatables: dict[str, Datatable] = {}

        self.outliers_settings = OutliersSettings(OutliersMode.OFF, 1.5)
        self.binning_settings = BinningSettings()

        self.report = ""

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def description(self) -> str:
        return self.metadata["description"]

    @property
    def source_path(self) -> str:
        return self.metadata["source_path"] if "source_path" in self.metadata else ""

    @property
    def experiment_started(self) -> pd.Timestamp:
        return pd.to_datetime(self.metadata["experiment_started"], utc=False).tz_localize(None)

    @property
    def experiment_stopped(self) -> pd.Timestamp:
        return pd.to_datetime(self.metadata["experiment_stopped"], utc=False).tz_localize(None)

    @property
    def experiment_duration(self) -> pd.Timedelta:
        return self.experiment_stopped - self.experiment_started

    def add_datatable(self, datatable: Datatable) -> None:
        self.datatables[datatable.name] = datatable

    def remove_datatable(self, datatable: Datatable) -> None:
        self.datatables.pop(datatable.name)

    def rename(self, name: str) -> None:
        self.metadata["name"] = name

    def extract_levels_from_property(self, property_name: str) -> dict[str, FactorLevel]:
        levels_dict: dict[str, list[str]] = {}
        for animal in self.animals.values():
            level_name = animal.properties[property_name]
            if level_name not in levels_dict:
                levels_dict[level_name] = []
            levels_dict[level_name].append(animal.id)

        levels: dict[str, FactorLevel] = {}
        index = 0
        for key, value in levels_dict.items():
            level = FactorLevel(
                name=key,
                color=get_color_hex(index),
                animal_ids=value,
            )
            levels[level.name] = level
            index += 1
        return levels

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        for datatable in self.datatables.values():
            datatable.rename_animal(old_id, animal)

        # Rename animal in factor's levels definitions
        for factor in self.factors.values():
            for level in factor.levels:
                for i, animal_id in enumerate(level.animal_ids):
                    if animal_id == old_id:
                        level.animal_ids[i] = animal.id

        # Rename animal in metadata
        new_dict = {}
        for item in self.metadata["animals"].values():
            if item["id"] == old_id:
                item["id"] = animal.id
            new_dict[item["id"]] = item
        self.metadata["animals"] = new_dict

        # Rename animal in dictionary
        self.animals.pop(old_id)
        self.animals[animal.id] = animal

        # messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        # Remove animals from factor's levels definitions
        for factor in self.factors.values():
            for level in factor.levels:
                level_set = set(level.animal_ids)
                filtered_set = level_set.difference(animal_ids)
                level.animal_ids = list(filtered_set)

        for animal_id in animal_ids:
            self.animals.pop(animal_id)

        if "animals" in self.metadata:
            new_meta_animals = {}
            for item in self.metadata["animals"].values():
                if item["id"] not in animal_ids:
                    new_meta_animals[item["id"]] = item
            self.metadata["animals"] = new_meta_animals

        for datatable in self.datatables.values():
            datatable.exclude_animals(animal_ids)

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        if range_start <= self.experiment_started < range_end:
            self.metadata["experiment_started"] = str(range_end)
        if range_start < self.experiment_stopped <= range_end:
            self.metadata["experiment_stopped"] = str(range_start)
        for datatable in self.datatables.values():
            datatable.exclude_time(range_start, range_end)

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.metadata["experiment_started"] = str(range_start)
        self.metadata["experiment_stopped"] = str(range_end)
        for datatable in self.datatables.values():
            datatable.trim_time(range_start, range_end)

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        for datatable in self.datatables.values():
            datatable.resample(resampling_interval)

    def set_factors(self, factors: dict[str, Factor]) -> None:
        self.factors = factors

        for datatable in self.datatables.values():
            datatable.set_factors(factors)

    def apply_binning(self, binning_settings: BinningSettings) -> None:
        self.binning_settings = binning_settings
        messaging.broadcast(messaging.BinningMessage(self, self, binning_settings))

    def apply_outliers(self, settings: OutliersSettings) -> None:
        self.outliers_settings = settings
        messaging.broadcast(messaging.DataChangedMessage(self, self))

    def clone(self):
        return deepcopy(self)

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        dataset_tree_item.clear()
        for datatable in self.datatables.values():
            dataset_tree_item.add_child(DatatableTreeItem(datatable))

    def __setstate__(self, state):
        self.__dict__.update(state)
        for datatable in self.datatables.values():
            # Recalculate active_df dataframes
            datatable.refresh_active_df()
