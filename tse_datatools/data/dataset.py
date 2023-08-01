from typing import Literal, Any, Optional

import numpy as np
import pandas as pd

from tse_datatools.data.animal import Animal
from tse_datatools.data.binning_settings import BinningSettings
from tse_datatools.data.box import Box
from tse_datatools.data.calo_details import CaloDetails
from tse_datatools.data.factor import Factor
from tse_datatools.data.group import Group
from tse_datatools.data.variable import Variable


class Dataset:
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict,
        boxes: dict[int, Box],
        animals: dict[int, Animal],
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        self.name = name
        self.path = path

        self.meta = meta

        self.boxes = boxes
        self.animals = animals
        self.variables = variables

        self.original_df = df
        self.active_df = self.original_df.copy()
        self.sampling_interval = sampling_interval

        self.factors: dict[str, Factor] = {}
        self.binning_settings = BinningSettings()

        self.calo_details: Optional[CaloDetails] = None

    @property
    def start_timestamp(self):
        first_value = self.original_df["DateTime"].iat[0]
        return first_value

    def extract_groups_from_field(self, field: Literal["text1", "text2", "text3"] = "text1") -> dict[str, Group]:
        """Extract groups assignment from Text1, Text2 or Text3 field"""
        groups_dict: dict[str, list[int]] = {}
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

    def filter_by_animals(self, animal_ids: list[int]) -> pd.DataFrame:
        df = self.active_df[self.active_df["Animal"].isin(animal_ids)]
        return df

    def filter_by_boxes(self, box_ids: list[int]) -> pd.DataFrame:
        df = self.active_df[self.active_df["Box"].isin(box_ids)]
        return df

    def filter_by_groups(self, groups: list[Group]) -> pd.DataFrame:
        group_ids = [group.name for group in groups]
        df = self.active_df[self.active_df["Group"].isin(group_ids)]
        df = df.dropna()
        return df

    def adjust_time(self, delta: str) -> pd.DataFrame:
        self.active_df["DateTime"] = self.active_df["DateTime"] + pd.Timedelta(delta)
        return self.active_df

    def set_factors(self, factors: dict[str, Factor]):
        self.factors = factors

        # TODO: should be copy?
        df = self.original_df.copy()

        animal_ids = df["Animal"].unique()

        for factor in self.factors.values():
            animal_factor_map: dict[int, Any] = {}
            for animal_id in animal_ids:
                animal_factor_map[animal_id] = None

            for group in factor.groups:
                for animal_id in group.animal_ids:
                    animal_factor_map[animal_id] = group.name

            df[factor.name] = df["Animal"]
            df[factor.name].replace(animal_factor_map, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

        self.active_df = df

    def refresh_active_df(self):
        self.set_factors(self.factors)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["active_df"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.refresh_active_df()
