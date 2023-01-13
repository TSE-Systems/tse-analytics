from typing import Optional

import pandas as pd

from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.binning_operation import BinningOperation


def calculate_grouped_data(
    df: pd.DataFrame,
    timedelta: pd.Timedelta,
    operation: BinningOperation,
    grouping_mode: GroupingMode,
    selected_variable: Optional[str] = None,
) -> pd.DataFrame:
    # Store initial column order
    cols = df.columns

    result = None
    if grouping_mode == GroupingMode.GROUPS:
        result = df.groupby(['Group', 'Run']).resample(timedelta, on='DateTime')
    elif grouping_mode == GroupingMode.ANIMALS:
        result = df.groupby(['Animal', 'Box', 'Group', 'Run']).resample(timedelta, on='DateTime')
    elif grouping_mode == GroupingMode.RUNS:
        result = df.groupby(['Run']).resample(timedelta, on='DateTime')

    errors = result.std(numeric_only=True)[selected_variable].to_numpy() if selected_variable is not None else None

    if operation == BinningOperation.MEAN:
        result = result.mean(numeric_only=True)
    elif operation == BinningOperation.MEDIAN:
        result = result.median(numeric_only=True)
    else:
        result = result.sum(numeric_only=True)

    if grouping_mode == GroupingMode.GROUPS:
        result.sort_values(by=['DateTime', 'Group'], inplace=True)
    elif grouping_mode == GroupingMode.ANIMALS:
        result.sort_values(by=['DateTime', 'Box'], inplace=True)
    elif grouping_mode == GroupingMode.RUNS:
        result.sort_values(by=['DateTime', 'Run'], inplace=True)

    # the inverse of groupby, reset_index
    result = result.reset_index().reindex(cols, axis=1)

    # Hide empty columns
    if grouping_mode == GroupingMode.GROUPS:
        result.drop(columns=['Animal', 'Box'], inplace=True)
    elif grouping_mode == GroupingMode.RUNS:
        result.drop(columns=['Animal', 'Box', 'Group'], inplace=True)

    start_date_time = result['DateTime'][0]
    result["Timedelta"] = result['DateTime'] - start_date_time
    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    result['Bin'] = result['Bin'].astype('category')

    if errors is not None:
        result['Std'] = errors

    return result
