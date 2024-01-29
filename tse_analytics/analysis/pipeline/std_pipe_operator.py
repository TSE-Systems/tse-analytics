import pandas as pd

from tse_analytics.analysis.pipeline.pipe_operator import PipeOperator


class STDPipeOperator(PipeOperator):
    def __init__(self, selected_variable: str):
        self.selected_variable = selected_variable

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        errors = df.std(numeric_only=True)[self.selected_variable]
        df["Std"] = errors
        return df
