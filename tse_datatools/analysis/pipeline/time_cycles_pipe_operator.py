from datetime import datetime

import pandas as pd

from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator


class TimeCyclesParams:
    def __init__(self, apply: bool, light_cycle_start: datetime.time, dark_cycle_start: datetime.time):
        self.apply = apply
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start


class TimeCyclesPipeOperator(PipeOperator):
    def __init__(self, params: TimeCyclesParams):
        self.params = params

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.params.apply:
            return df

        filter_method = (
            lambda x: "Light" if (self.params.light_cycle_start <= x.time() < self.params.dark_cycle_start) else "Dark"
        )
        df["Cycle"] = df["DateTime"].apply(filter_method).astype("category")
        return df
