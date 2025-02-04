import pandas as pd

from tse_analytics.core.data.shared import Variable


class TraffiCageData:
    def __init__(
        self,
        dataset,
        name: str,
        path: str,
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        self.dataset = dataset
        self.name = name
        self.path = path
        self.variables = variables
        self.raw_df = df
        self.sampling_interval = sampling_interval

        self.device_ids: list[int] = []

        self.df = self.raw_df.copy()

        self._preprocess()

    @property
    def start_timestamp(self):
        return self.raw_df.at[0, "DateTime"]

    def _preprocess(self):
        # Rename table columns
        self.df.rename(columns={
            "BoxNo": "Box",
            "ChannelNo": "Channel",
            "Channel type": "ChannelType",
        }, inplace=True)

        self.device_ids = self.df["Box"].unique().tolist()
        self.device_ids.sort()

        box_to_animal_map = {}
        for animal in self.dataset.animals.values():
            box_to_animal_map[animal.box] = animal.id

        self.df.insert(
            self.df.columns.get_loc("Box") + 1,
            "Animal",
            self.df["Box"],
        )
        self.df.replace({"Animal": box_to_animal_map}, inplace=True)

        # Sanitize Tag column
        self.df["Tag"] = self.df["Tag"].str.removeprefix("RFID ")

        self.df.sort_values(["DateTime"], inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        # convert categorical types
        self.df = self.df.astype({
            "Animal": "category",
            "ChannelType": "category",
            "Tag": "category",
        })
