import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


EXTENSION_NAME = "RunningWheel"


class RunningWheelData(ExtensionData):
    def __init__(
        self,
        dataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        super().__init__(
            dataset,
            name,
            raw_data,
            dataset.devices[EXTENSION_NAME],
        )

    def preprocess_data(self) -> None:
        df = self.raw_data["Registration"].copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = self.dataset.get_tag_to_name_map()
        df["Animal"] = df["Tag"].replace(tag_to_animal_map)

        # Convert cumulative values to differential ones
        preprocessed_device_df = []
        device_ids = df["DeviceId"].unique().tolist()
        for i, device_id in enumerate(device_ids):
            device_data = df[df["DeviceId"] == device_id]
            device_data["Left"] = device_data["Left"].diff().fillna(df["Left"])
            device_data["Right"] = device_data["Right"].diff().fillna(df["Right"])
            preprocessed_device_df.append(device_data)
        df = pd.concat(preprocessed_device_df, ignore_index=True, sort=False)

        # Rename columns
        df.rename(
            columns={
                "Time": "DateTime",
            },
            inplace=True,
        )

        # Drop the non-necessary columns
        df.drop(
            columns=[
                "DeviceId",
                "Tag",
                "Reset",
            ],
            inplace=True,
        )

        # Remove records without animal assignment
        df.dropna(subset=["Animal"], inplace=True)

        variables = {
            "Left": Variable(
                "Left",
                "count",
                "RunningWheel left rotations counter",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "Right": Variable(
                "Right",
                "count",
                "RunningWheel right rotations counter",
                "int64",
                Aggregation.SUM,
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
        })

        datatable = Datatable(
            self.dataset,
            EXTENSION_NAME,
            f"{EXTENSION_NAME} main table",
            variables,
            df,
            None,
        )

        self.dataset.add_datatable(datatable)

    def get_csv_data(
        self,
        export_registrations: bool,
        export_variables: bool,
    ) -> tuple[str, dict[str, pd.DataFrame]]:
        result: dict[str, pd.DataFrame] = {}

        tag_to_animal_map = self.dataset.get_tag_to_name_map()

        if export_registrations:
            data = {
                "DateTime": [],
                "DeviceType": EXTENSION_NAME,
                "DeviceId": [],
                "AnimalName": [],
                "AnimalTag": [],
                "TableType": "Registration",
                "Left": [],
                "Right": [],
                "Reset": [],
            }

            for row in self.raw_data["Registration"].itertuples():
                data["DateTime"].append(row.Time)
                data["DeviceId"].append(row.DeviceId)
                data["AnimalName"].append(tag_to_animal_map[row.Tag] if row.Tag == row.Tag else "")
                data["AnimalTag"].append(row.Tag if row.Tag == row.Tag else "")

                data["Left"].append(row.Left)
                data["Right"].append(row.Right)
                data["Reset"].append(row.Reset)

            result["Registration"] = pd.DataFrame(data)

        if export_variables:
            variables_csv_data = self.get_variables_csv_data(EXTENSION_NAME, tag_to_animal_map)
            result.update(variables_csv_data)

        return EXTENSION_NAME, result
