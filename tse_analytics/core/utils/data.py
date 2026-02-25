"""Data transform utilities."""

from datetime import time

import pandas as pd

from tse_analytics.core.data.shared import SplitMode


def get_group_by_params(group_by_str: str) -> tuple[SplitMode, str]:
    # Convert group_by string to SplitMode and factor_name
    match group_by_str:
        case SplitMode.ANIMAL.value:
            return SplitMode.ANIMAL, ""
        case SplitMode.RUN.value:
            return SplitMode.RUN, ""
        case SplitMode.TOTAL.value:
            return SplitMode.TOTAL, ""
        case _:
            return SplitMode.FACTOR, group_by_str


def time_to_float(value: time) -> float:
    """Convert a time object to a float representing hours.

    This function converts a datetime.time object to a float value representing
    the time in hours, with minutes converted to a fractional part of an hour.
    For example, 2:30 PM would be converted to 14.5.

    Args:
        value: The time object to convert.

    Returns:
        A float representing the time in hours.
    """
    return value.hour + value.minute / 60.0


def exclude_animals_from_df(df: pd.DataFrame, animal_ids: set[str]) -> pd.DataFrame:
    df = df[~df["Animal"].isin(animal_ids)]
    df["Animal"] = df["Animal"].cat.remove_unused_categories()
    df.reset_index(inplace=True, drop=True)
    return df
