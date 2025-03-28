import numpy as np
import pandas as pd

from tse_analytics.core.data.shared import Animal


def rename_animal_df(df: pd.DataFrame, old_id: str, animal: Animal) -> pd.DataFrame:
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
    df["Bin"] = (df["Timedelta"] / sampling_interval).round().astype(int)
    return df


def normalize_nd_array(input: np.ndarray):
    min_value = np.min(input)
    max_value = np.max(input)
    return (input - min_value) / (max_value - min_value)
