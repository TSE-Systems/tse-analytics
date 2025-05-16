import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


EXTENSION_NAME = "AnimalGate"


class AnimalGateData(ExtensionData):
    def __init__(
        self,
        dataset: "IntelliMazeDataset",
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        super().__init__(
            dataset,
            name,
            raw_data,
            dataset.devices[EXTENSION_NAME],
        )

    def get_combined_datatable(self) -> Datatable:
        df = self.raw_data["Sessions"].copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = {}
        for animal in self.dataset.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id
        df["Animal"] = df["Tag"].replace(tag_to_animal_map)

        # Add duration column
        df["Duration"] = (df["End"] - df["Start"]).dt.total_seconds()

        # Rename columns
        df.rename(
            columns={
                "Start": "DateTime",
            },
            inplace=True,
        )

        # Drop the non-necessary columns
        df.drop(
            columns=[
                "End",
                "DeviceId",
                "Tag",
            ],
            inplace=True,
        )

        variables = {
            "Duration": Variable(
                "Duration",
                "sec",
                "AnimalGate session duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
            "Weight": Variable(
                "Weight",
                "g",
                "AnimalGate weight",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.dataset.experiment_started
        df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

        # Convert types
        df = df.astype({
            "Animal": "category",
            "Direction": "category",
        })

        datatable = Datatable(
            self.dataset,
            "AnimalGate",
            "AnimalGate main table",
            variables,
            df,
            None,
        )

        return datatable
