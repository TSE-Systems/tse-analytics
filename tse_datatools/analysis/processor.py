from typing import Literal

import pandas as pd


def apply_time_binning(
    df: pd.DataFrame,
    delta: int,
    unit_name: Literal["day", "hour", "minute"],
    mode: Literal["sum", "mean", "median"]
) -> pd.DataFrame:
    unit = "H"
    if unit_name == "day":
        unit = "D"
    elif unit_name == "hour":
        unit = "H"
    elif unit_name == "minute":
        unit = "min"
    rule = f'{delta}{unit}'

    if mode == "mean":
        result = df.resample(rule, on='DateTime', origin="start").mean()
    elif mode == "median":
        result = df.resample(rule, on='DateTime', origin="start").median()
    else:
        result = df.resample(rule, on='DateTime', origin="start").sum()

    result["Order"] = result.index - result.index[0]
    return result
