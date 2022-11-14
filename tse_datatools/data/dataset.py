from typing import Literal

import numpy as np
import pandas as pd

from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
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
        sampling_interval: pd.Timedelta
    ):
        self.name = name
        self.path = path

        self.meta = meta

        self.boxes = boxes
        self.animals = animals
        self.variables = variables

        self.df = df
        self.sampling_interval = sampling_interval

        self.groups: dict[str, Group] = {}

    def extract_groups_from_field(self, field: Literal["text1", "text2", "text3"] = "text1") -> dict[str, Group]:
        """Extract groups assignment from Text1, Text2 or Text3 field"""
        groups_dict = {}
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
        df = self.df[self.df['Animal'].isin(animal_ids)]
        return df

    def filter_by_boxes(self, box_ids: list[int]) -> pd.DataFrame:
        df = self.df[self.df['Box'].isin(box_ids)]
        return df

    def filter_by_groups(self, groups: list[Group]) -> pd.DataFrame:
        group_ids = [group.name for group in groups]
        df = self.df[self.df['Group'].isin(group_ids)]
        df = df.dropna()
        return df

    def calculate_groups_data(self, binning_params: BinningParams) -> pd.DataFrame:
        df = self.df.copy()

        # Store initial column order
        cols = df.columns

        result = df.groupby('Group', dropna=True).resample(binning_params.timedelta, on='DateTime')

        if binning_params.operation == "mean":
            result = result.mean(numeric_only=True)
        elif binning_params.operation == "median":
            result = result.median(numeric_only=True)
        else:
            result = result.sum(numeric_only=True)

        # the inverse of groupby, reset_index
        result.sort_values(by=['DateTime', 'Group'], inplace=True)
        result = result.reset_index().reindex(cols, axis=1)
        # Hide empty columns
        result.drop(columns=['Animal', 'Box'], inplace=True)

        start_date_time = result['DateTime'][0]
        result["Timedelta"] = result['DateTime'] - start_date_time
        result["Bin"] = (result["Timedelta"] / binning_params.timedelta).round().astype(int)
        result['Bin'] = result['Bin'].astype('category')
        return result

    def adjust_time(self, delta: str) -> pd.DataFrame:
        self.df['DateTime'] = self.df['DateTime'] + pd.Timedelta(delta)
        return self.df

    def set_groups(self, groups: dict[str, Group]):
        self.groups = groups

        # TODO: should be copy?
        df = self.df

        animal_group_map = {}
        animal_ids = df["Animal"].unique()
        for animal_id in animal_ids:
            animal_group_map[animal_id] = np.NaN

        for group in groups.values():
            for animal_id in group.animal_ids:
                animal_group_map[animal_id] = group.name

        df["Group"] = df["Animal"]
        df["Group"].replace(animal_group_map, inplace=True)
        df["Group"] = df["Group"].astype('category')

        self.df = df

    def export_to_excel(self, path: str):
        with pd.ExcelWriter(path) as writer:
            self.df.to_excel(writer, sheet_name='Data')

    def __getstate__(self):
        state = self.__dict__.copy()
        return state
