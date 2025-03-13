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


def reassign_df_timedelta_and_bin(df: pd.DataFrame, sampling_interval: pd.Timedelta) -> pd.DataFrame:
    df.reset_index(inplace=True, drop=True)

    # Get unique runs numbers
    runs = df["Run"].unique().tolist()

    # Reassign timedeltas
    for run in runs:
        # Get start timestamp per run
        start_date_time = df[df["Run"] == run]["DateTime"].iloc[0]
        df.loc[df["Run"] == run, "Timedelta"] = df["DateTime"] - start_date_time

    # Reassign bins numbers
    df["Bin"] = (df["Timedelta"] / sampling_interval).round().astype(int)
    return df


def export_df_to_excel(df: pd.DataFrame, path: str) -> None:
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="Data")


def export_to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, sep=";", index=False)
