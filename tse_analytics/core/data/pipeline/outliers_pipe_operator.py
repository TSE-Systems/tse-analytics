import pandas as pd

from tse_analytics.core.data.outliers import OutliersParams
from tse_analytics.core.data.shared import Variable


def process_outliers(df: pd.DataFrame, settings: OutliersParams, variables: dict[str, Variable]) -> pd.DataFrame:
    remove_outliers_for_vars = {key: value for (key, value) in variables.items() if value.remove_outliers}

    if len(remove_outliers_for_vars) == 0:
        return df

    vars = list(remove_outliers_for_vars)

    # Calculate quantiles and IQR
    q1 = df[vars].quantile(0.25, numeric_only=True)
    q3 = df[vars].quantile(0.75, numeric_only=True)
    iqr = q3 - q1

    # Return a boolean array of the rows with (any) non-outlier column values
    condition = ~((df[vars] < (q1 - settings.coefficient * iqr)) | (df[vars] > (q3 + settings.coefficient * iqr))).any(
        axis=1
    )

    # Filter our dataframe based on condition
    result = df[condition]

    result.reset_index(inplace=True)

    return result
