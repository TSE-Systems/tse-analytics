from datetime import timedelta
from typing import Literal

import pandas as pd
from pandas import Timedelta

from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
from tse_datatools.data.group import Group
from tse_datatools.data.variable import Variable


class Dataset:
    def __init__(self, name: str, path: str, meta: dict, boxes: dict[int, Box], animals: dict[int, Animal], variables: dict[str, Variable], df: pd.DataFrame):
        self.name = name
        self.path = path

        self.meta = meta

        self.boxes = boxes
        self.animals = animals
        self.variables = variables
        self.df = df

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
        df = self.df[self.df['AnimalNo'].isin(animal_ids)]
        return df

    def filter_by_groups(self, groups: list[Group]) -> pd.DataFrame:
        df = self.df.copy()

        animal_group_map = {}
        animal_ids = df["AnimalNo"].unique()
        for animal_id in animal_ids:
            animal_group_map[animal_id] = None

        for group in groups:
            for animal_id in group.animal_ids:
                animal_group_map[animal_id] = group.name

        df["Group"] = df["AnimalNo"]
        df["Group"].replace(animal_group_map, inplace=True)
        df = df.dropna()
        return df

    def adjust_time(self, delta: str) -> pd.DataFrame:
        self.df['DateTime'] = self.df['DateTime'] + Timedelta(delta)
        return self.df

    def __getstate__(self):
        state = self.__dict__.copy()
        return state
