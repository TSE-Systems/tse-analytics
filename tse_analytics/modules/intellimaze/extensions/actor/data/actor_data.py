import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData
from tse_analytics.modules.intellimaze.data.utils import get_combined_variables_table

EXTENSION_NAME = "Actor"


class ActorData(ExtensionData):
    """
    Class for handling Actor extension data.

    This class extends the base ExtensionData class to provide functionality specific
    to Actor devices. It processes raw data from Actor measurements
    and provides methods for data analysis and export.

    Attributes:
        Inherits all attributes from ExtensionData.
    """

    def __init__(
        self,
        dataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        """
        Initialize an ActorData object.

        Args:
            dataset: The parent dataset.
            name (str): The name of the extension.
            raw_data (dict[str, pd.DataFrame]): Dictionary mapping data types to DataFrames.
        """
        super().__init__(
            dataset,
            name,
            raw_data,
            dataset.devices[EXTENSION_NAME],
        )

    def preprocess_data(self) -> None:
        df = self.raw_data["State"].copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = self.dataset.get_tag_to_name_map()
        df["Animal"] = df["AnimalTag"].replace(tag_to_animal_map)

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
                "AnimalTag",
            ],
            inplace=True,
        )

        # Remove records without animal assignment
        df.dropna(subset=["Animal"], inplace=True)

        variables = {
            "Mode": Variable(
                "Mode",
                "category",
                "Actor mode",
                str,
                Aggregation.SUM,
                False,
            ),
            "State": Variable(
                "State",
                "category",
                "Actor state",
                str,
                Aggregation.SUM,
                False,
            ),
        }

        # Merge variables tables
        variables_table = get_combined_variables_table(self)
        if not variables_table.empty:
            df = pd.concat([df, variables_table], ignore_index=True, sort=False)

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.dataset.experiment_started
        df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

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
        """
        Get CSV data for export.

        This method prepares data for export to CSV format. It can export both
        state data and variable data.

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
            # Skip actor state data
            pass

        if export_variables:
            variables_csv_data = self.get_variables_csv_data(EXTENSION_NAME, tag_to_animal_map)
            result.update(variables_csv_data)

        return EXTENSION_NAME, result
