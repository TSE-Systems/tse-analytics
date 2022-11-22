import pandas as pd

from tse_analytics.core.view_mode import ViewMode


def calculate_grouped_data(
    df: pd.DataFrame,
    timedelta: pd.Timedelta,
    operation: str,
    view_mode: ViewMode
) -> pd.DataFrame:
    # Store initial column order
    cols = df.columns

    result = None
    if view_mode == ViewMode.GROUPS:
        result = df.groupby('Group').resample(timedelta, on='DateTime')
    elif view_mode == ViewMode.ANIMALS:
        result = df.groupby(['Animal', 'Box']).resample(timedelta, on='DateTime')

    if operation == "mean":
        result = result.mean(numeric_only=True)
    elif operation == "median":
        result = result.median(numeric_only=True)
    else:
        result = result.sum(numeric_only=True)

    if view_mode == ViewMode.GROUPS:
        result.sort_values(by=['DateTime', 'Group'], inplace=True)
    elif view_mode == ViewMode.ANIMALS:
        result.sort_values(by=['DateTime', 'Box'], inplace=True)

    # the inverse of groupby, reset_index
    result = result.reset_index().reindex(cols, axis=1)

    # Hide empty columns
    if view_mode == ViewMode.GROUPS:
        result.drop(columns=['Animal', 'Box'], inplace=True)

    start_date_time = result['DateTime'][0]
    result["Timedelta"] = result['DateTime'] - start_date_time
    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    result['Bin'] = result['Bin'].astype('category')

    return result
