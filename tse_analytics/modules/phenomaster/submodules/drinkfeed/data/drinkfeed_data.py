import pandas as pd

from tse_analytics.core.data.shared import Variable


class DrinkFeedData:
    def __init__(
        self,
        dataset,
        name: str,
        path: str,
        variables: dict[str, Variable],
        df: pd.DataFrame,
    ):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.variables = variables
        self.raw_df = df

    @property
    def start_timestamp(self):
        return self.raw_df.at[0, "DateTime"]
