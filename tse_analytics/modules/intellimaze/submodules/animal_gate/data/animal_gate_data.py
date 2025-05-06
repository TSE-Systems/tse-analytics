import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-AG"


class AnimalGateData:
    def __init__(
        self,
        dataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data

        self.device_ids = dataset.devices["AnimalGate"]
        self.device_ids.sort()

    def get_raw_data(self):
        return self.raw_data

    def get_device_ids(self):
        return self.device_ids

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.raw_data["Sessions"].copy()

        df[f"Duration{DATA_SUFFIX}"] = (df["End"] - df["Start"]).dt.total_seconds()

        tag_to_animal_map = {}
        for animal in self.dataset.animals.values():
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

        # Set column order
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
