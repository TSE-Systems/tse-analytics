"""
Module containing helper functions for data manipulation.

This module provides utility functions for common data manipulation tasks,
such as renaming animals in a DataFrame, reassigning timedelta and bin values,
and normalizing arrays.
"""

import numpy as np
import pandas as pd

from tse_analytics.core.data.shared import Animal


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
        "Animal": str,
    })
    df.loc[df["Animal"] == old_id, "Animal"] = animal.id
    df = df.astype({
        "Animal": "category",
    })
    return df


def reassign_df_timedelta_and_bin(
    df: pd.DataFrame, sampling_interval: pd.Timedelta, merging_mode: str | None
) -> pd.DataFrame:
    """
    Reassign timedelta and bin values in a DataFrame.

    This function recalculates timedelta values based on the merging mode and
    reassigns bin numbers based on the sampling interval.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.
    sampling_interval : pd.Timedelta or None
        The sampling interval for bin calculation.
    merging_mode : str or None
        The merging mode, which affects how timedeltas are calculated.

    Returns
    -------
    pd.DataFrame
        The DataFrame with reassigned timedelta and bin values.
    """
    df.reset_index(inplace=True, drop=True)

    if merging_mode == "overlap":
        # Get unique runs numbers
        runs = df["Run"].unique().tolist()

        # Reassign timedeltas
        for run in runs:
            # Get start timestamp per run
            start_date_time = df[df["Run"] == run]["DateTime"].iloc[0]
            df.loc[df["Run"] == run, "Timedelta"] = df["DateTime"] - start_date_time
    else:
        start_date_time = df["DateTime"].iloc[0]
        df["Timedelta"] = df["DateTime"] - start_date_time

    # Reassign bins numbers
    if sampling_interval is not None:
        df["Bin"] = (df["Timedelta"] / sampling_interval).round().astype(int)
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
