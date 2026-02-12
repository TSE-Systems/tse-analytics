from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


class ExtensionData:
    """
    Base class for IntelliMaze extension data.

    This class provides a common interface for handling data from different IntelliMaze extensions.
    It stores raw data and device information, and provides methods for data processing and export.

    Attributes:
        dataset (IntelliMazeDataset): The parent dataset.
        name (str): The name of the extension.
        raw_data (dict[str, pd.DataFrame]): Dictionary mapping data types to DataFrames.
        device_ids (list[str]): List of device IDs associated with this extension.
    """

    def __init__(
        self,
        dataset: IntelliMazeDataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
        device_ids: list[str],
    ):
        """
        Initialize an ExtensionData object.

        Args:
            dataset (IntelliMazeDataset): The parent dataset.
            name (str): The name of the extension.
            raw_data (dict[str, pd.DataFrame]): Dictionary mapping data types to DataFrames.
            device_ids (list[str]): List of device IDs associated with this extension.
        """
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data
        self.device_ids = device_ids
        self.device_ids.sort()

    def get_raw_data(self):
        """
        Get the raw data for this extension.

        Returns:
            dict[str, pd.DataFrame]: Dictionary mapping data types to DataFrames.
        """
        return self.raw_data

    def get_device_ids(self):
        """
        Get the device IDs associated with this extension.

        Returns:
            list[str]: List of device IDs.
        """
        return self.device_ids

    def preprocess_data(self) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def get_csv_data(self, export_registrations: bool, export_variables: bool) -> tuple[str, dict[str, pd.DataFrame]]:
        """
        Get CSV data for export.

        This method must be implemented by subclasses.

        Args:
            export_registrations (bool): Whether to export registrations.
            export_variables (bool): Whether to export variables.

        Returns:
            tuple[str, dict[str, pd.DataFrame]]: A tuple containing the extension name and a dictionary
                mapping data types to DataFrames.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def get_variables_csv_data(self, extension_name: str, tag_to_animal_map: dict[str, str]) -> dict[str, pd.DataFrame]:
        """
        Get CSV data for variables.

        This method converts variable data to a format suitable for CSV export.

        Args:
            extension_name (str): The name of the extension.
            tag_to_animal_map (dict[str, str]): Dictionary mapping animal tags to animal IDs.

        Returns:
            dict[str, pd.DataFrame]: Dictionary mapping variable types to DataFrames.
        """
        result: dict[str, pd.DataFrame] = {}

        variables_dict = {
            "DoubleVariables": "Doubles",
            "IntegerVariables": "Integers",
            "BooleanVariables": "Booleans",
        }

        for name, type in variables_dict.items():
            if name in self.raw_data:
                data: dict[str, list | str] = {
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
