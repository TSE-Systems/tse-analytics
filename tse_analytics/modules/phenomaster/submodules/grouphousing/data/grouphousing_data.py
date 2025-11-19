import math

import pandas as pd

from tse_analytics.modules.phenomaster.submodules.grouphousing.trafficage_config import TRAFFICAGE_POSITIONS


def _calculate_distance(row: pd.Series):
    if pd.isna(row["PreviousChannelType"]):
        return None
    loc1 = TRAFFICAGE_POSITIONS[row["ChannelType"]]
    loc2 = TRAFFICAGE_POSITIONS[row["PreviousChannelType"]]
    distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    return distance


class GroupHousingData:
    def __init__(
        self,
        dataset,
        name: str,
        path: str,
        df: pd.DataFrame,
    ):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.raw_df = df

        self.animal_ids = df["Animal"].unique().tolist()
        self.animal_ids.sort()

    @property
    def start_timestamp(self):
        return self.raw_df.at[0, "StartDateTime"]

    def get_preprocessed_data(
        self,
        remove_repeating_records: bool,
        remove_overlapping: bool,
        overlapping_ms: int | None,
    ) -> dict[str, pd.DataFrame]:
        df = self.raw_df.copy()

        # convert categorical types
        df = df.astype({
            "Animal": "category",
            "ChannelType": "category",
        })

        # Split data by antenna type
        all_df = self._preprocess_df(df, remove_repeating_records)
        trafficage_df = self._preprocess_df(df[df["Channel"] > 3], remove_repeating_records)
        drinkfeed_df = self._preprocess_df(df[df["Channel"] < 4], remove_repeating_records)

        # Preprocess TraffiCage data
        trafficage_df["Distance"] = trafficage_df.apply(_calculate_distance, axis=1)
        # Detect overlapping records
        for animal in self.animal_ids:
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

    def _preprocess_df(self, df: pd.DataFrame, remove_repeating_records: bool) -> pd.DataFrame:
        df.sort_values(["Animal", "StartDateTime"], inplace=True)

        if remove_repeating_records:
            # Remove repeating neighbor rows
            drop = df[df["Animal"].eq(df["Animal"].shift()) & df["Channel"].eq(df["Channel"].shift())].index
            df.drop(drop, inplace=True)

        for animal in self.animal_ids:
            df.loc[df["Animal"] == animal, "PreviousChannelType"] = df[df["Animal"] == animal]["ChannelType"].shift()

        df["Activity"] = df.groupby("Animal", observed=False).cumcount()

        df.sort_values(by=["StartDateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
