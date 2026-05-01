"""
Pipeline operator for grouping data by columns based on split mode.

This module provides a function for grouping a DataFrame by different columns
based on the specified split mode (by animal, factor, run, or total).
"""

import pandas as pd

from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import Variable


def group_by_columns(
    df: pd.DataFrame,
    variables: dict[str, Variable],
    group_settings: GroupingSettings,
) -> pd.DataFrame:
    if group_settings.mode == GroupingMode.ANIMAL:
        # No grouping needed
        return df

    match group_settings.mode:
        case GroupingMode.FACTOR:
            group_by = ["Bin", group_settings.factor_name]
        case GroupingMode.RUN:
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
    # TODO: check if done properly
    result.reset_index(inplace=True)

    return result
