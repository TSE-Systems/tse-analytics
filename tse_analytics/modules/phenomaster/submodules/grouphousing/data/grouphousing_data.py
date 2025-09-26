import pandas as pd


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
        return self.raw_df.at[0, "DateTime"]

    def get_preprocessed_data(self, remove_repeating_records: bool) -> dict[str, pd.DataFrame]:
        df = self.raw_df.copy()

        # convert categorical types
        df = df.astype({
            "Animal": "category",
            "ChannelType": "category",
        })

        # Split data by antenna type
        all_df = self._preprocess_df(df, remove_repeating_records)
        trafficage_df = self._preprocess_df(df[df["Channel"] > 4], remove_repeating_records)
        drinkfeed_df = self._preprocess_df(df[df["Channel"] < 5], remove_repeating_records)

        return {
            "All": all_df,
            "TraffiCage": trafficage_df,
            "DrinkFeed": drinkfeed_df,
        }

    def _preprocess_df(self, df: pd.DataFrame, remove_repeating_records: bool) -> pd.DataFrame:
        df.sort_values(["Animal", "DateTime"], inplace=True)

        if remove_repeating_records:
            # Remove repeating neighbor rows
            drop = df[df["Animal"].eq(df["Animal"].shift()) & df["Channel"].eq(df["Channel"].shift())].index
            df.drop(drop, inplace=True)

        df["PreviousChannelType"] = df[df["Animal"].eq(df["Animal"].shift())]["ChannelType"].shift()
        df["Activity"] = df.groupby("Animal", observed=False).cumcount()

        df.sort_values(by=["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
