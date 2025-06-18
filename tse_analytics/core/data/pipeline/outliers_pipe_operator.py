"""
Pipeline operator for processing outliers in a DataFrame.

This module provides a function for detecting and removing outliers from a DataFrame
using the Interquartile Range (IQR) method.
"""

import pandas as pd

from tse_analytics.core.data.outliers import OutliersSettings
from tse_analytics.core.data.shared import Variable


def process_outliers(df: pd.DataFrame, settings: OutliersSettings, variables: dict[str, Variable]) -> pd.DataFrame:
    """
    Process outliers in a DataFrame using the IQR method.

    This function identifies outliers in the specified variables using the IQR method
    and removes rows containing outliers from the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.
    settings : OutliersSettings
        Settings for outlier detection, including the coefficient for IQR.
    variables : dict[str, Variable]
        Dictionary mapping variable names to Variable objects.

    Returns
    -------
    pd.DataFrame
        A DataFrame with outliers removed.
    """
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

    result.reset_index(drop=True, inplace=True)

    return result
