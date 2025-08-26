import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


EXTENSION_NAME = "OperantDevice"


class OperantDeviceData(ExtensionData):
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

    def preprocess_data(self) -> None:
        df = self.raw_data["Sessions"].copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = self.dataset.get_tag_to_name_map()
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
        """
        Get CSV data for export.

        This method prepares data for export to CSV format. It can export both
        registration data (sessions) and variable data.

        Args:
            export_registrations (bool): Whether to export registration data.
            export_variables (bool): Whether to export variable data.

        Returns:
            tuple[str, dict[str, pd.DataFrame]]: A tuple containing the extension name and a dictionary
                mapping data types to DataFrames ready for CSV export.
        """
        result: dict[str, pd.DataFrame] = {}

        tag_to_animal_map = self.dataset.get_tag_to_name_map()

        if export_registrations:
            data: dict[str, list | str] = {
                "DateTime": [],
                "DeviceType": EXTENSION_NAME,
                "DeviceId": [],
                "AnimalName": [],
                "AnimalTag": [],
                "TableType": "Sessions",
                "Direction": [],
                "Start": [],
                "End": [],
                "Duration": [],
                "Weight": [],
                "IdSectionVisited": [],
                "StandbySectionVisited": [],
            }

            for row in self.raw_data["Sessions"].itertuples():
                data["DateTime"].append(row.End if row.Direction == "Out" else row.Start)
                data["DeviceId"].append(row.DeviceId)
                data["AnimalName"].append(tag_to_animal_map[row.Tag] if row.Tag == row.Tag else "")
                data["AnimalTag"].append(row.Tag if row.Tag == row.Tag else "")

                data["Direction"].append(row.Direction)
                data["Start"].append(row.Start)
                data["End"].append(row.End)
                data["Duration"].append((row.End - row.Start).total_seconds())
                data["Weight"].append(row.Weight)
                data["IdSectionVisited"].append(row.IdSectionVisited)
                data["StandbySectionVisited"].append(row.StandbySectionVisited)

            result["Sessions"] = pd.DataFrame(data)

        if export_variables:
            variables_csv_data = self.get_variables_csv_data(EXTENSION_NAME, tag_to_animal_map)
            result.update(variables_csv_data)

        return EXTENSION_NAME, result
