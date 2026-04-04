"""
ConsumptionScale extension data handling for IntelliMaze experiments.

This module provides functionality for processing and analyzing data from ConsumptionScale devices
in IntelliMaze experiments. It defines the ConsumptionScaleData class which extends the base
ExtensionData class to handle ConsumptionScale specific data.
"""

import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.data.utils import get_combined_variables_table, get_variables_csv_data

EXTENSION_NAME = "ConsumptionScale"


def preprocess_data(
    dataset: IntelliMazeDataset,
    extension_data: dict[str, Datatable],
) -> None:
    df = extension_data["Consumption"].df.copy()

    # Replace animal tags with animal IDs
    tag_to_animal_map = dataset.get_tag_to_name_map()
    df["Animal"] = df["Tag"].replace(tag_to_animal_map)

    # Convert cumulative values to differential ones
    preprocessed_device_df = []
    device_ids = df["DeviceId"].unique().tolist()
    for _, device_id in enumerate(device_ids):
        device_data = df[df["DeviceId"] == device_id]
        device_data["Consumption"] = device_data["Consumption"].diff().fillna(df["Consumption"]).round(5)
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
        ],
        inplace=True,
    )

    # Remove records without animal assignment
    df.dropna(subset=["Animal"], inplace=True)

    variables = {
        "Consumption": Variable(
            "Consumption",
            "g",
            "ConsumptionScale intake",
            "float64",
            Aggregation.SUM,
            False,
        ),
    }

    # Merge variables tables
    variables_table = get_combined_variables_table(dataset, extension_data)
    if not variables_table.empty:
        df = pd.concat([df, variables_table], ignore_index=True, sort=False)

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta column
    experiment_started = dataset.experiment_started
    df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

    # Convert types
    df = df.astype({
        "Animal": "category",
    })

    datatable = Datatable(
        dataset,
        EXTENSION_NAME,
        f"{EXTENSION_NAME} main table",
        variables,
        df,
        {
            "origin": EXTENSION_NAME,
        },
    )

    dataset.add_datatable(datatable)


def get_csv_data(
    dataset: IntelliMazeDataset,
    extension_data: dict[str, Datatable],
    export_registrations: bool,
    export_variables: bool,
) -> tuple[str, dict[str, pd.DataFrame]]:
    """
    Get CSV data for export.

    This method prepares data for export to CSV format. It can export both
    registration data (consumption measurements) and variable data.

    Args:
        export_registrations (bool): Whether to export registration data.
        export_variables (bool): Whether to export variable data.

    Returns:
        tuple[str, dict[str, pd.DataFrame]]: A tuple containing the extension name and a dictionary
            mapping data types to DataFrames ready for CSV export.
    """
    result: dict[str, pd.DataFrame] = {}

    tag_to_animal_map = dataset.get_tag_to_name_map()

    if export_registrations:
        data = {
            "DateTime": [],
            "DeviceType": EXTENSION_NAME,
            "DeviceId": [],
            "AnimalName": [],
            "AnimalTag": [],
            "TableType": "Consumption",
            "Consumption": [],
        }

        for row in extension_data["Consumption"].df.itertuples():
            data["DateTime"].append(row.Time)
            data["DeviceId"].append(row.DeviceId)
            data["AnimalName"].append(tag_to_animal_map[row.Tag] if row.Tag == row.Tag else "")
            data["AnimalTag"].append(row.Tag if row.Tag == row.Tag else "")

            data["Consumption"].append(row.Consumption)

        result["Consumption"] = pd.DataFrame(data)

    if export_variables:
        variables_csv_data = get_variables_csv_data(extension_data, EXTENSION_NAME, tag_to_animal_map)
        result.update(variables_csv_data)

    return EXTENSION_NAME, result
