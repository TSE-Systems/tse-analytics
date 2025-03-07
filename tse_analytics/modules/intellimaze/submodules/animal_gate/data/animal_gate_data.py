import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-AG"


class AnimalGateData:
    def __init__(
        self,
        im_dataset,
        name: str,
        sessions_df: pd.DataFrame,
        antenna_df: pd.DataFrame,
        log_df: pd.DataFrame,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame,
    ):
        self.im_dataset = im_dataset
        self.name = name
        self.device_ids: list[str] = im_dataset.devices["AnimalGate"]

        self.sessions_df = sessions_df
        self.antenna_df = antenna_df
        self.log_df = log_df
        self.input_df = input_df
        self.output_df = output_df

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.sessions_df.copy()

        df[f"Duration{DATA_SUFFIX}"] = (df["End"] - df["Start"]).dt.total_seconds()

        tag_to_animal_map = {}
        for animal in self.im_dataset.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id

        # Replace animal tags with animal IDs
        df["Tag"] = df["Tag"].replace(tag_to_animal_map)

        df.rename(
            columns={
                "Start": "DateTime",
                "Tag": "Animal",
                "Weight": f"Weight{DATA_SUFFIX}",
            },
            inplace=True,
        )

        df.drop(
            columns=[
                "DeviceId",
                "Direction",
                "End",
                "IdSectionVisited",
                "StandbySectionVisited",
            ],
            inplace=True,
        )

        # Set columns order
        df = df[["DateTime", "Animal", f"Duration{DATA_SUFFIX}", f"Weight{DATA_SUFFIX}"]]

        variables = {
            f"Duration{DATA_SUFFIX}": Variable(
                f"Duration{DATA_SUFFIX}",
                "sec",
                "AnimalGate session duration",
                "float64",
                Aggregation.MEAN,
                False,
            ),
            f"Weight{DATA_SUFFIX}": Variable(
                f"Weight{DATA_SUFFIX}",
                "g",
                "AnimalGate weight",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, variables
