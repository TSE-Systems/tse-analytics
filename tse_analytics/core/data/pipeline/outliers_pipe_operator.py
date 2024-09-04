import pandas as pd

from tse_analytics.core.data.outliers import OutliersParams


def process_outliers(df: pd.DataFrame, settings: OutliersParams, variables: list[str]) -> pd.DataFrame:
    # Calculate quantiles and IQR
    q1 = df[variables].quantile(0.25, numeric_only=True)
    q3 = df[variables].quantile(0.75, numeric_only=True)
    iqr = q3 - q1

    # Return a boolean array of the rows with (any) non-outlier column values
    condition = ~(
        (df[variables] < (q1 - settings.coefficient * iqr)) | (df[variables] > (q3 + settings.coefficient * iqr))
    ).any(axis=1)

    # Filter our dataframe based on condition
    result = df[condition]

    return result
