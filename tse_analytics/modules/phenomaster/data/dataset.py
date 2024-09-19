from copy import deepcopy
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

import pandas as pd

from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.shared import Animal, Factor, Group, Variable
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails


class Dataset:
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict | list[dict],
        animals: dict[str, Animal],
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        self.id = uuid4()
        self.name = name
        self.path = path
        self.meta = meta

        self.animals = animals
        self.variables = variables

        self.original_df = df
        self.active_df = self.original_df.copy()
        self.sampling_interval = sampling_interval

        self.factors: dict[str, Factor] = {}
        self.binning_settings = BinningSettings()

        self.calo_details: CaloDetails | None = None
        self.meal_details: MealDetails | None = None
        self.actimot_details: ActimotDetails | None = None

        self.report = ""

    @property
    def start_timestamp(self) -> pd.Timestamp:
        first_value = self.original_df.at[0, "DateTime"]
        return first_value

    @property
    def end_timestamp(self) -> pd.Timestamp:
        last_value = self.original_df.at[self.original_df.index[-1], "DateTime"]
        return last_value

    @property
    def duration(self) -> pd.Timedelta:
        return self.end_timestamp - self.start_timestamp

    def extract_groups_from_field(self, field: Literal["text1", "text2", "text3"] = "text1") -> dict[str, Group]:
        """Extract groups assignment from Text1, Text2 or Text3 field"""
        groups_dict: dict[str, list[str]] = {}
        for animal in self.animals.values():
            group_name = getattr(animal, field)
            if group_name not in groups_dict:
                groups_dict[group_name] = []
            groups_dict[group_name].append(animal.id)

        groups: dict[str, Group] = {}
        for key, value in groups_dict.items():
            group = Group(key, value)
            groups[group.name] = group
        return groups

    def _rename_animal_df(self, df: pd.DataFrame, old_id: str, animal: Animal) -> pd.DataFrame:
        df = df.astype({
            "Animal": str,
        })
        df.loc[df["Animal"] == old_id, "Animal"] = animal.id
        df = df.astype({
            "Animal": "category",
        })
        return df

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.original_df = self._rename_animal_df(self.original_df, old_id, animal)
        self.active_df = self._rename_animal_df(self.active_df, old_id, animal)

        if self.meal_details is not None:
            self.meal_details.raw_df = self._rename_animal_df(self.meal_details.raw_df, old_id, animal)
        if self.calo_details is not None:
            self.calo_details.raw_df = self._rename_animal_df(self.calo_details.raw_df, old_id, animal)
        if self.actimot_details is not None:
            self.actimot_details.raw_df = self._rename_animal_df(self.actimot_details.raw_df, old_id, animal)

        # Rename animal in factor's groups definitions
        for factor in self.factors.values():
            for group in factor.groups:
                for i, animal_id in enumerate(group.animal_ids):
                    if animal_id == old_id:
                        group.animal_ids[i] = animal.id

        # Rename animal in metadata
        new_dict = {}
        for item in self.meta["animals"].values():
            if item["id"] == old_id:
                item["id"] = animal.id
            new_dict[item["id"]] = item
        self.meta["animals"] = new_dict

        # Rename animal in dictionary
        self.animals.pop(old_id)
        self.animals[animal.id] = animal

    def exclude_animals(self, animal_ids: set[str]) -> None:
        # Remove animals from factor's groups definitions
        for factor in self.factors.values():
            for group in factor.groups:
                group_set = set(group.animal_ids)
                filtered_set = group_set.difference(animal_ids)
                group.animal_ids = list(filtered_set)

        for animal_id in animal_ids:
            self.animals.pop(animal_id)

        new_meta_animals = {}
        for item in self.meta["animals"].values():
            if item["id"] not in animal_ids:
                new_meta_animals[item["id"]] = item
        self.meta["animals"] = new_meta_animals

        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.original_df.reset_index(inplace=True)

        self.active_df = self.active_df[~self.active_df["Animal"].isin(animal_ids)]
        self.active_df.reset_index(inplace=True)

        if self.calo_details is not None:
            self.calo_details.raw_df = self.calo_details.raw_df[~self.calo_details.raw_df["Animal"].isin(animal_ids)]
        if self.meal_details is not None:
            self.meal_details.raw_df = self.meal_details.raw_df[~self.meal_details.raw_df["Animal"].isin(animal_ids)]
        if self.actimot_details is not None:
            self.actimot_details.raw_df = self.actimot_details.raw_df[
                ~self.actimot_details.raw_df["Animal"].isin(animal_ids)
            ]

    def _reassign_df_timedelta_and_bin(self, df: pd.DataFrame, sampling_interval: pd.Timedelta) -> pd.DataFrame:
        df.reset_index(inplace=True)
        # Reassign bin and timedelta
        start_date_time = df.at[0, "DateTime"]
        df["Timedelta"] = df["DateTime"] - start_date_time
        df["Bin"] = (df["Timedelta"] / sampling_interval).round().astype(int)
        return df

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._exclude_df_time(self.original_df, range_start, range_end)
        self.active_df = self._exclude_df_time(self.active_df, range_start, range_end)

    def _exclude_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] < range_start) | (df["DateTime"] > range_end)]
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._trim_df_time(self.original_df, range_start, range_end)
        self.active_df = self._trim_df_time(self.active_df, range_start, range_end)

    def _trim_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] >= range_start) & (df["DateTime"] <= range_end)]
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]

        agg = {
            "DateTime": "first",
            "Box": "first",
            "Run": "first",
        }
        for column in self.original_df.columns:
            if column not in default_columns:
                if self.original_df.dtypes[column].name != "category":
                    agg[column] = "mean"

        group_by = ["Animal"]
        sort_by = ["Timedelta", "Box"]

        original_result = self.original_df.groupby(group_by, dropna=False, observed=False)
        original_result = original_result.resample(resampling_interval, on="Timedelta", origin="start").agg(agg)

        original_result.sort_values(by=sort_by, inplace=True)

        original_result = self._reassign_df_timedelta_and_bin(original_result, resampling_interval)

        self.sampling_interval = resampling_interval
        self.original_df = original_result

        self.refresh_active_df()

    def adjust_time(self, delta: pd.Timedelta) -> None:
        self.original_df = self._adjust_df_time(self.original_df, delta)
        self.active_df = self._adjust_df_time(self.active_df, delta)

    def _adjust_df_time(self, df: pd.DataFrame, delta: pd.Timedelta) -> pd.DataFrame:
        df["DateTime"] = df["DateTime"] + delta
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def set_factors(self, factors: dict[str, Factor]):
        self.factors = factors

        # TODO: should be copy?
        df = self.original_df.copy()

        animal_ids = df["Animal"].unique()

        for factor in self.factors.values():
            animal_factor_map: dict[str, Any] = {}
            for animal_id in animal_ids:
                animal_factor_map[animal_id] = pd.NA

            for group in factor.groups:
                for animal_id in group.animal_ids:
                    animal_factor_map[animal_id] = group.name

            df[factor.name] = df["Animal"].astype(str)
            # df[factor.name].replace(animal_factor_map, inplace=True)
            # df[factor.name] = df[factor.name].replace(animal_factor_map)
            df.replace({factor.name: animal_factor_map}, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

        self.active_df = df

    def refresh_active_df(self) -> None:
        self.set_factors(self.factors)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["active_df"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.refresh_active_df()

    def clone(self):
        return deepcopy(self)
