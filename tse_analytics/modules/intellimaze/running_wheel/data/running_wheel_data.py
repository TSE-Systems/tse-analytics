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

        # df.sort_values(["DateTime"], inplace=True)
        #
        # df['DateTime'] = df['DateTime'].dt.tz_localize(None)
        # df['DateTime'] = df['DateTime'].dt.floor('Min')
        #
        # original_result = df.groupby("Animal", dropna=False, observed=False)
        # original_result = original_result.resample("1min", on="DateTime", origin="start").mean()
        # original_result.reset_index(inplace=True, drop=False)
        # original_result.sort_values(by=["Animal", "DateTime"], inplace=True)
        #
        # date_range = pd.date_range(self.im_dataset.experiment_started.round("T"), self.im_dataset.experiment_stopped.round("T"), freq="T")
        #
        # original_result.set_index("DateTime", inplace=True, drop=False)
        #
        # tmp = original_result[original_result["Animal"] == "Animal 1"]
        #
        # df_regular = tmp.reindex(date_range)
        #
        # df.reset_index(drop=True, inplace=True)

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, variables
