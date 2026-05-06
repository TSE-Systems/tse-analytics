"""Data transform utilities."""

from datetime import time

import numpy as np
import pandas as pd

from tse_analytics.core.data.shared import Animal

_dtypes_name_mapping = {
    "int8": "Int8",
    "int16": "Int16",
    "int32": "Int32",
    "int64": "Int64",
    "uint8": "UInt8",
    "uint16": "UInt16",
    "uint32": "UInt32",
    "uint64": "UInt64",
    "float16": "Float16",
    "float32": "Float32",
    "float64": "Float64",
    "bool": "boolean",
    "str": "string",
}


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


def sanitize_dtypes(dtypes: dict[str, str]) -> dict[str, str]:
    for key, value in dtypes.items():
        if value in _dtypes_name_mapping:
            dtypes[key] = _dtypes_name_mapping[value]
    return dtypes


def rename_animal_df(df: pd.DataFrame, old_id: str, animal: Animal) -> pd.DataFrame:
    """
    Rename an animal in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing animal data.
    old_id : str
        The current ID of the animal.
    animal : Animal
        The animal object with the new ID.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the animal renamed.
    """
    df = df.astype({
        "Animal": "string",
    })
    df.loc[df["Animal"] == old_id, "Animal"] = animal.id
    df = df.astype({
        "Animal": "category",
    })
    return df


def reassign_df_timedelta(df: pd.DataFrame, merging_mode: str | None) -> pd.DataFrame:
    """
    Reassign timedelta values in a DataFrame.

    This function recalculates timedelta values based on the merging mode.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.
    merging_mode : str or None
        The merging mode, which affects how timedeltas are calculated.

    Returns
    -------
    pd.DataFrame
        The DataFrame with reassigned timedelta values.
    """
    df.reset_index(inplace=True, drop=True)

    if merging_mode == "overlap":
        # Get unique experiment numbers
        experiments = df["Experiment"].unique().tolist()

        # Reassign timedeltas
        for experiment in experiments:
            # Get start timestamp per experiment
            start_date_time = df[df["Experiment"] == experiment]["DateTime"].iloc[0]
            df.loc[df["Experiment"] == experiment, "Timedelta"] = df["DateTime"] - start_date_time
    else:
        start_date_time = df["DateTime"].iloc[0]
        df["Timedelta"] = df["DateTime"] - start_date_time

    return df


def normalize_nd_array(input: np.ndarray):
    """
    Normalize a NumPy array to the range [0, 1].

    Parameters
    ----------
    input : np.ndarray
        The input array to normalize.

    Returns
    -------
    np.ndarray
        The normalized array with values in the range [0, 1].
    """
    min_value = np.min(input)
    max_value = np.max(input)
    return (input - min_value) / (max_value - min_value)
