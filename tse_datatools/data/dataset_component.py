import pandas as pd

from tse_datatools.data.group import Group
from tse_datatools.data.variable import Variable


class DatasetComponent:
    def __init__(self, name: str, path: str, meta: dict, df: pd.DataFrame, variables: dict[str, Variable]):
        self.name = name
        self.path = path
        self.meta = meta
        self.df = df
        self.variables = variables

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
