import pandas as pd

from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_bin_data import DrinkFeedBinData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings

default_columns = ["DateTime", "Animal", "Box"]


def process_drinkfeed_intervals(
    drinkfeed_data: DrinkFeedBinData,
    long_df: pd.DataFrame,
    settings: DrinkFeedSettings,
    diets_dict: dict[int, float],
):
    # TODO: drop unnecessary rows
    long_df = long_df.loc[~(long_df["Value"] == 0)]

    long_df.sort_values(by=["DateTime"], inplace=True)
    long_df.reset_index(drop=True, inplace=True)

    group_by = ["Animal", "Sensor"]
    grouped = long_df.groupby(group_by, dropna=False, observed=False)

    timedelta = pd.Timedelta(
        hours=settings.fixed_interval.hour,
        minutes=settings.fixed_interval.minute,
        seconds=settings.fixed_interval.second,
    )

    intervals_df = grouped.resample(timedelta, on="DateTime", origin="start").aggregate({
        "Value": "sum",
    })

    intervals_df.sort_values(by=["DateTime", "Animal"], inplace=True)
    intervals_df.reset_index(inplace=True)

    sensors = intervals_df["Sensor"].unique().tolist()

    intervals_df = intervals_df.pivot(index=["Animal", "DateTime"], columns="Sensor", values="Value")
    intervals_df.reset_index(inplace=True)

    # Calculate time delta
    first_timestamp = intervals_df["DateTime"].min()
    if first_timestamp > drinkfeed_data.dataset.experiment_started:
        first_timestamp = drinkfeed_data.dataset.experiment_started
    intervals_df.insert(
        intervals_df.columns.get_loc("DateTime") + 1, "Timedelta", intervals_df["DateTime"] - first_timestamp
    )

    # Insert Bin column
    intervals_df.insert(
        intervals_df.columns.get_loc("Timedelta") + 1,
        "Bin",
        (intervals_df["Timedelta"] / timedelta).round().astype(int),
    )

    # Add caloric value column
    for sensor in sensors:
        if "Feed" in sensor:
            _add_caloric_column(intervals_df, sensor, diets_dict)

    return intervals_df


def _add_caloric_column(df: pd.DataFrame, origin_column: str, diets_dict: dict[int, float]) -> pd.DataFrame:
    if origin_column in df.columns:
        df.insert(df.columns.get_loc(origin_column) + 1, f"{origin_column}-kcal", df["Animal"])
        df.replace({f"{origin_column}-kcal": diets_dict}, inplace=True)
        df[f"{origin_column}-kcal"] = df[f"{origin_column}-kcal"].astype(float)
        df[f"{origin_column}-kcal"] = df[f"{origin_column}-kcal"] * df[origin_column]
    return df
