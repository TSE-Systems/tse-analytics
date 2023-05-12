import pandas as pd

from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator


class FilterPipeOperator(PipeOperator):
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
