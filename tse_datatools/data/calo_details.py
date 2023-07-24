import pandas as pd

from tse_datatools.data.variable import Variable


class CaloDetails:
    def __init__(
        self,
        dataset,
        name: str,
        path: str,
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.variables = variables
        self.raw_df = df
        self.sampling_interval = sampling_interval

    @property
    def start_timestamp(self):
        first_value = self.raw_df["DateTime"].iat[0]
        return first_value

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
