import pandas as pd

from tse_analytics.core.data.datatable import Datatable


class ExtensionData:
    def __init__(
        self,
        dataset: "IntelliMazeDataset",
        name: str,
        raw_data: dict[str, pd.DataFrame],
        device_ids: list[str],
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data
        self.device_ids = device_ids
        self.device_ids.sort()

    def get_raw_data(self):
        return self.raw_data

    def get_device_ids(self):
        return self.device_ids

    def preprocess_data(self) -> None:
        main_datatable = self.get_combined_datatable()
        self.dataset.add_datatable(main_datatable)

    def get_combined_datatable(self) -> Datatable:
        raise NotImplementedError("Subclasses must implement this method")

    def get_csv_data(self, export_registrations: bool, export_variables: bool) -> tuple[str, dict[str, pd.DataFrame]]:
        raise NotImplementedError("Subclasses must implement this method")

    def get_variables_csv_data(self, extension_name: str, tag_to_animal_map: dict[str, str]) -> dict[str, pd.DataFrame]:
        result: dict[str, pd.DataFrame] = {}

        variables_dict = {
            "DoubleVariables": "Doubles",
            "IntegerVariables": "Integers",
            "BooleanVariables": "Booleans",
        }

        for name, type in variables_dict.items():
            if name in self.raw_data:
                data = {
                    "DateTime": [],
                    "DeviceType": extension_name,
                    "DeviceId": [],
                    "AnimalName": [],
                    "AnimalTag": [],
                    "TableType": type,
                    "Name": [],
                    "Data": [],
                }

                for row in self.raw_data[name].itertuples():
                    data["DateTime"].append(row.Time)
                    data["DeviceId"].append(row.DeviceId)
                    data["AnimalName"].append(tag_to_animal_map[row.Tag] if row.Tag == row.Tag else "")
                    data["AnimalTag"].append(row.Tag if row.Tag == row.Tag else "")

                    data["Name"].append(row.Name)
                    data["Data"].append(row.Data)

                result[name] = pd.DataFrame(data)

        return result
