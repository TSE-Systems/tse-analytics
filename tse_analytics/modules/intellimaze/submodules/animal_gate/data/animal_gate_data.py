import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable


class AnimalGateData:
    def __init__(
        self,
        dataset: "IntelliMazeDataset",
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

    def preprocess_data(self) -> None:
        main_datatable = self._get_main_datatable()
        self.dataset.add_datatable(main_datatable)

    def _get_main_datatable(self) -> Datatable:
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
            ],
            inplace=True,
        )

        variables = {
            f"Duration": Variable(
                f"Duration",
                "sec",
                "AnimalGate session duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
            f"Weight": Variable(
                f"Weight",
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
