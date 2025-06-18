"""
Pipeline operator for grouping data by columns based on split mode.

This module provides a function for grouping a DataFrame by different columns
based on the specified split mode (by animal, factor, run, or total).
"""

import pandas as pd

from tse_analytics.core.data.shared import Variable, SplitMode


def group_by_columns(
    df: pd.DataFrame, variables: dict[str, Variable], split_mode: SplitMode, selected_factor_name: str
) -> pd.DataFrame:
    """
    Group a DataFrame by columns based on the specified split mode.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to group.
    variables : dict[str, Variable]
        Dictionary mapping variable names to Variable objects.
    split_mode : SplitMode
        The mode to use for splitting the data (by animal, factor, run, or total).
    selected_factor_name : str
        The name of the factor to use when split_mode is FACTOR.

    Returns
    -------
    pd.DataFrame
        A grouped DataFrame with appropriate aggregations applied.
    """
    if split_mode == SplitMode.ANIMAL:
        # No grouping needed
        return df

    match split_mode:
        case SplitMode.FACTOR:
            group_by = ["Bin", selected_factor_name]
        case SplitMode.RUN:
            group_by = ["Bin", "Run"]
        case _:  # Total split mode
            group_by = ["Bin"]

    aggregation = {}

    if "DateTime" in df.columns:
        aggregation["DateTime"] = "first"

    if "Timedelta" in df.columns:
        aggregation["Timedelta"] = "first"

    # TODO: use means only when aggregating in split modes!
    for variable in variables.values():
        aggregation[variable.name] = "mean"

    result = df.groupby(group_by, dropna=False, observed=False).aggregate(aggregation)
    result.reset_index(inplace=True)

    return result
