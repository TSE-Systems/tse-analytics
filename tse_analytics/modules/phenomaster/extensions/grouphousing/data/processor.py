import math
from datetime import datetime

import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.extensions.grouphousing.trafficage_config import TRAFFICAGE_POSITIONS


def preprocess_trafficage_datatable(dataset: Dataset, df: pd.DataFrame) -> Datatable:
    df = df.copy()

    # Rename columns to be compatible with Datatable format
    df.rename(columns={"StartDateTime": "DateTime"}, inplace=True)
    df.drop(columns=["EndDateTime"], inplace=True)

    # Calculate time delta
    first_timestamp = df["DateTime"].min()
    if first_timestamp > dataset.experiment_started:
        first_timestamp = dataset.experiment_started
    df.insert(df.columns.get_loc("DateTime") + 1, "Timedelta", df["DateTime"] - first_timestamp)

    now = datetime.now()
    now_string = now.strftime("%Y-%m-%d %H:%M:%S")

    variables = {
        "Activity": Variable(
            "Activity",
            "[cnt]",
            "Activity index",
            "int64",
            Aggregation.MAX,
            False,
        ),
        "Distance": Variable(
            "Distance",
            "",
            "Relative distance",
            "float64",
            Aggregation.SUM,
            False,
        ),
    }

    datatable = Datatable(
        dataset,
        f"TraffiCage [{now_string}]",
        "TraffiCage data",
        variables,
        df,
        {
            "origin": "TraffiCage",
        },
    )

    datatable.set_factors(dataset.factors)

    return datatable


def get_preprocessed_data(
    datatable: Datatable,
    remove_repeating_records: bool,
    remove_overlapping: bool,
    overlapping_ms: int | None,
) -> dict[str, pd.DataFrame]:
    df = datatable.df.copy()

    # convert categorical types
    df = df.astype({
        "Animal": "category",
        "ChannelType": "category",
    })

    # Split data by an antenna type
    all_df = _preprocess_df(datatable, df, remove_repeating_records)
    trafficage_df = _preprocess_df(datatable, df[df["Channel"] > 3], remove_repeating_records)
    drinkfeed_df = _preprocess_df(datatable, df[df["Channel"] < 4], remove_repeating_records)

    # Preprocess TraffiCage data
    trafficage_df["Distance"] = trafficage_df.apply(_calculate_distance, axis=1)
    # Detect overlapping records
    animal_ids = datatable.metadata.get("animal_ids")
    for animal in animal_ids:
        trafficage_df.loc[trafficage_df["Animal"] == animal, "TimeDiff"] = trafficage_df[
            trafficage_df["Animal"] == animal
        ]["StartDateTime"].diff(2)
        trafficage_df.loc[trafficage_df["Animal"] == animal, "ChannelDiff"] = trafficage_df[
            trafficage_df["Animal"] == animal
        ]["Channel"].diff(2)

    if remove_overlapping:
        trafficage_df = trafficage_df[
            ~(
                (trafficage_df["ChannelDiff"] == 0)
                & (trafficage_df["TimeDiff"] < pd.Timedelta(milliseconds=overlapping_ms))
            )
        ]
        # Recalculate activity
        trafficage_df["Activity"] = trafficage_df.groupby("Animal", observed=False).cumcount()

    return {
        "All": all_df,
        "TraffiCage": trafficage_df,
        "DrinkFeed": drinkfeed_df,
    }


def _preprocess_df(
    datatable: Datatable,
    df: pd.DataFrame,
    remove_repeating_records: bool,
) -> pd.DataFrame:
    df.sort_values(["Animal", "StartDateTime"], inplace=True)

    if remove_repeating_records:
        # Remove repeating neighbor rows
        drop = df[df["Animal"].eq(df["Animal"].shift()) & df["Channel"].eq(df["Channel"].shift())].index
        df.drop(drop, inplace=True)

    animal_ids = datatable.metadata.get("animal_ids")
    for animal in animal_ids:
        df.loc[df["Animal"] == animal, "PreviousChannelType"] = df[df["Animal"] == animal]["ChannelType"].shift()

    df["Activity"] = df.groupby("Animal", observed=False).cumcount()

    df.sort_values(by=["StartDateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _calculate_distance(row: pd.Series) -> float | None:
    if pd.isna(row["PreviousChannelType"]):
        return None
    loc1 = TRAFFICAGE_POSITIONS[row["ChannelType"]]
    loc2 = TRAFFICAGE_POSITIONS[row["PreviousChannelType"]]
    distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    return distance
