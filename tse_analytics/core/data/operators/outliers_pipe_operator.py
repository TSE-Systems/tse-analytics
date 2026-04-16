"""
Pipeline operator for processing outliers in a DataFrame.

This module provides a function for detecting and removing outliers from a DataFrame
using the Interquartile Range (IQR) method.
"""

import pandas as pd

from tse_analytics.core.data.outliers import OutliersSettings, OutliersType
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
    remove_outliers_for_vars = {key: variable for (key, variable) in variables.items() if variable.remove_outliers}

    if len(remove_outliers_for_vars) == 0:
        return df

    vars = list(remove_outliers_for_vars)

    is_outlier = None
    match settings.type:
        case OutliersType.IQR:
            # Calculate quantiles and IQR
            q1 = df[vars].quantile(0.25, numeric_only=True)
            q3 = df[vars].quantile(0.75, numeric_only=True)
            iqr = q3 - q1

            lower = q1 - settings.iqr_multiplier * iqr
            upper = q3 + settings.iqr_multiplier * iqr

            # Return a boolean array of the rows with (any) outlier column values
            is_outlier = (df[vars] < lower) | (df[vars] > upper)
        case OutliersType.ZSCORE:
            z_score = (df[vars] - df[vars].mean()) / df[vars].std()
            is_outlier = z_score.abs() > 3
        case OutliersType.THRESHOLDS:
            if settings.min_threshold_enabled and settings.max_threshold_enabled:
                is_outlier = (df[vars] < settings.min_threshold) | (df[vars] > settings.max_threshold)
            elif settings.min_threshold_enabled:
                is_outlier = df[vars] < settings.min_threshold
            elif settings.max_threshold_enabled:
                is_outlier = df[vars] > settings.max_threshold

    if is_outlier is None:
        return df

    # # Drop rows that contain any outlier in the flagged variables
    # any_outlier = is_outlier.any(axis=1)
    # df = df.loc[~any_outlier].copy()

    # Filter our dataframe based on a condition
    df[vars] = df[vars].mask(is_outlier)

    df.reset_index(drop=True, inplace=True)

    return df
