import pandas as pd

from tse_analytics.core.data.shared import Variable, Aggregation

DATA_SUFFIX = "-RW"


class RunningWheelData:
    def __init__(
        self,
        im_dataset,
        name: str,
        registration_df: pd.DataFrame,
        model_df: pd.DataFrame,
    ):
        self.im_dataset = im_dataset
        self.name = name
        self.device_ids: list[str] = im_dataset.devices["RunningWheel"]

        self.registration_df = registration_df
        self.model_df = model_df

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.registration_df.copy()

        tag_to_animal_map = {}
        for animal in self.im_dataset.animals.values():
            tag_to_animal_map[animal.text1] = animal.id

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

        # df.set_index("DateTime", inplace=True, drop=False)
        # df = df.resample("1min").fillna(method='ffill')

        df.reset_index(drop=True, inplace=True)

        return df, variables
