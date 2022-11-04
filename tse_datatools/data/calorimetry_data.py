import pandas as pd

from tse_datatools.data.dataset_component import DatasetComponent
from tse_datatools.data.variable import Variable


class CalorimetryData(DatasetComponent):
    def __init__(self, name: str, path: str, meta: dict, df: pd.DataFrame, variables: dict[str, Variable]):
        super().__init__(name, path, meta, df, variables)
