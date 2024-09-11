import pandas as pd

from tse_analytics.core.data.shared import Variable


class ActimotDetails:
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
        return self.raw_df.at[0, "DateTime"]
