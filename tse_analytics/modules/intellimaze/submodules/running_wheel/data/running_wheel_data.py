import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-RW"


class RunningWheelData:
    def __init__(
        self,
        dataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data

        self.device_ids = dataset.devices["RunningWheel"]
        self.device_ids.sort()

    def get_raw_data(self):
        return self.raw_data

    def get_device_ids(self):
        return self.device_ids

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.raw_data["Registration"].copy()

        # Convert cumulative values to differential ones
        preprocessed_device_df = []
        device_ids = df["DeviceId"].unique().tolist()
        for i, device_id in enumerate(device_ids):
            device_data = df[df["DeviceId"] == device_id]
            device_data["Left"] = device_data["Left"].diff().fillna(df["Left"])
            device_data["Right"] = device_data["Right"].diff().fillna(df["Right"])
            preprocessed_device_df.append(device_data)
        df = pd.concat(preprocessed_device_df, ignore_index=True, sort=False)

        tag_to_animal_map = {}
        for animal in self.dataset.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id

        # Replace animal tags with animal IDs
        df["Tag"] = df["Tag"].replace(tag_to_animal_map)

        df.rename(
            columns={
                "Time": "DateTime",
                "Tag": "Animal",
                "Left": f"Left{DATA_SUFFIX}",
                "Right": f"Right{DATA_SUFFIX}",
            },
            inplace=True,
        )

        df.drop(
            columns=[
                "DeviceId",
                "Reset",
            ],
            inplace=True,
        )

        # Remove records without animal assignment
        df.dropna(subset=["Animal"], inplace=True)

        # Set columns order
        df = df[["DateTime", "Animal", f"Left{DATA_SUFFIX}", f"Right{DATA_SUFFIX}"]]

        variables = {
            f"Left{DATA_SUFFIX}": Variable(
                f"Left{DATA_SUFFIX}",
                "count",
                "RunningWheel left rotations counter",
                "int64",
                Aggregation.SUM,
                False,
            ),
            f"Right{DATA_SUFFIX}": Variable(
                f"Right{DATA_SUFFIX}",
                "count",
                "RunningWheel right rotations counter",
                "int64",
                Aggregation.SUM,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, variables
