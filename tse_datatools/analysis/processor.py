from typing import Literal

import pandas as pd


def apply_time_binning(
    df: pd.DataFrame,
    delta: int,
    unit_name: Literal["day", "hour", "minute"],
    mode: Literal["sum", "mean", "median"]
) -> pd.DataFrame:
    # Store initial column order
    cols = df.columns

    unit = "H"
    if unit_name == "day":
        unit = "D"
    elif unit_name == "hour":
        unit = "H"
    elif unit_name == "minute":
        unit = "min"

    timedelta = pd.Timedelta(f'{delta}{unit}')

    result = df.groupby(['Animal', 'Box']).resample(timedelta, on='DateTime')

    if mode == "mean":
        result = result.mean(numeric_only=True)
    elif mode == "median":
        result = result.median(numeric_only=True)
    else:
        result = result.sum(numeric_only=True)

    # the inverse of groupby, reset_index
    result.sort_values(by=['DateTime', 'Box'], inplace=True)
    result = result.reset_index().reindex(cols, axis=1)

    start_date_time = result['DateTime'][0]
    result["Timedelta"] = result['DateTime'] - start_date_time
    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    return result
