import pandas as pd

from tse_datatools.analysis.outliers_params import OutliersParams
from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator


class OutliersPipeOperator(PipeOperator):
    def __init__(self, settings: OutliersParams, variables: list[str]):
        self.settings = settings
        self.variables = variables

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        # Calculate quantiles and IQR
        q1 = df[self.variables].quantile(0.25, numeric_only=True)
        q3 = df[self.variables].quantile(0.75, numeric_only=True)
        iqr = q3 - q1

        # Return a boolean array of the rows with (any) non-outlier column values
        condition = ~(
            (df[self.variables] < (q1 - self.settings.coefficient * iqr))
            | (df[self.variables] > (q3 + self.settings.coefficient * iqr))
        ).any(axis=1)

        # Filter our dataframe based on condition
        result = df[condition]

        return result
