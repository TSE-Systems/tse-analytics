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

    def get_preprocessed_data(self) -> dict[str, pd.DataFrame]:
        df = self.raw_df.copy()

        # Remove repeating neighbor rows
        df.sort_values(["Animal", "DateTime"], inplace=True)
        drop = df[df["Animal"].eq(df["Animal"].shift()) & df["Channel"].eq(df["Channel"].shift())].index
        df.drop(drop, inplace=True)

        # Sort again by DateTime
        df.sort_values(by=["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        df["Activity"] = df.groupby("Animal").cumcount()

        # convert categorical types
        df = df.astype({
            "Animal": "category",
            "ChannelType": "category",
        })

        # Split dataframes by antenna type
        trafficage_df = df[df["Channel"] > 4]
        trafficage_df["Activity"] = trafficage_df.groupby("Animal").cumcount()
        trafficage_df.reset_index(drop=True, inplace=True)

        drinkfeed_df = df[df["Channel"] < 5]
        drinkfeed_df.drop(columns=["Activity"], inplace=True)
        drinkfeed_df.reset_index(drop=True, inplace=True)

        return {
            "All": df,
            "TraffiCage": trafficage_df,
            "DrinkFeed": drinkfeed_df,
        }
