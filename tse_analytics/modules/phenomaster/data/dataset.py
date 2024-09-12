from copy import deepcopy
from datetime import datetime
from typing import Any, Literal

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

    @property
    def runs_count(self) -> int | None:
        return self.active_df["Run"].value_counts().count()

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
        if "Animals" in self.meta:
            for item in self.meta["Animals"]:
                if item["id"] == old_id:
                    item["id"] = animal.id
        elif "animals" in self.meta:
            new_dict = {}
            for item in self.meta["animals"].values():
                if item["id"] == old_id:
                    item["id"] = animal.id
                new_dict[item["id"]] = item
            self.meta["animals"] = new_dict

        # Rename animal in dictionary
        self.animals.pop(old_id)
        self.animals[animal.id] = animal

    def exclude_animals(self, animal_ids: list[str]) -> None:
        # Remove animals from factor's groups definitions
        for factor in self.factors.values():
            for group in factor.groups:
                group_set = set(group.animal_ids)
                filtered_set = group_set.difference(animal_ids)
                group.animal_ids = list(filtered_set)

        for animal_id in animal_ids:
            self.animals.pop(animal_id)

        new_meta_animals = []
        for item in self.meta["Animals"]:
            if item["id"] not in animal_ids:
                new_meta_animals.append(item)
        self.meta["Animals"] = new_meta_animals

        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.active_df = self.active_df[~self.active_df["Animal"].isin(animal_ids)]
        if self.calo_details is not None:
            self.calo_details.raw_df = self.calo_details.raw_df[~self.calo_details.raw_df["Animal"].isin(animal_ids)]
        if self.meal_details is not None:
            self.meal_details.raw_df = self.meal_details.raw_df[~self.meal_details.raw_df["Animal"].isin(animal_ids)]
        if self.actimot_details is not None:
            self.actimot_details.raw_df = self.actimot_details.raw_df[
                ~self.actimot_details.raw_df["Animal"].isin(animal_ids)
            ]

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self.original_df[
            (self.original_df["DateTime"] < range_start) | (self.original_df["DateTime"] > range_end)
        ]
        self.active_df = self.active_df[
            (self.active_df["DateTime"] < range_start) | (self.active_df["DateTime"] > range_end)
        ]

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self.original_df[
            (self.original_df["DateTime"] >= range_start) & (self.original_df["DateTime"] <= range_end)
        ]
        self.active_df = self.active_df[
            (self.active_df["DateTime"] >= range_start) & (self.active_df["DateTime"] <= range_end)
        ]

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        group_by = ["Animal", "Box", "Run"]

        original_result = self.original_df.groupby(group_by, dropna=False, observed=False)
        original_result = original_result.resample(resampling_interval, on="DateTime", origin="start").mean(
            numeric_only=True
        )
        original_result.sort_values(by=["DateTime", "Box"], inplace=True)
        # the inverse of groupby, reset_index
        original_result = original_result.reset_index()
        original_result["Timedelta"] = original_result["DateTime"] - original_result["DateTime"].iloc[0]
        original_result["Bin"] = (original_result["Timedelta"] / resampling_interval).round().astype(int)
        self.original_df = original_result.astype({"Bin": "category"})

        self.sampling_interval = resampling_interval

        self.refresh_active_df()

    def filter_by_groups(self, groups: list[Group]) -> pd.DataFrame:
        group_ids = [group.name for group in groups]
        df = self.active_df[self.active_df["Group"].isin(group_ids)]
        df = df.dropna()
        return df

    def adjust_time(self, delta: pd.Timedelta) -> None:
        self.original_df["DateTime"] = self.original_df["DateTime"] + delta
        self.active_df["DateTime"] = self.active_df["DateTime"] + delta

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
