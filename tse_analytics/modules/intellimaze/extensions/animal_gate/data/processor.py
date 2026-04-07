"""
AnimalGate extension data handling for IntelliMaze experiments.

This module provides functionality for processing and analyzing data from AnimalGate devices
in IntelliMaze experiments. It defines the AnimalGateData class which extends the base
ExtensionData class to handle AnimalGate specific data.
"""

import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.utils import get_tag_to_name_map, get_variables_csv_data

EXTENSION_NAME = "AnimalGate"


def preprocess_data(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
) -> None:
    df = extension_data["Sessions"].df.copy()

    # Replace animal tags with animal IDs
    tag_to_animal_map = get_tag_to_name_map(dataset.animals)
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
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "Weight": Variable(
            "Weight",
            "g",
            "AnimalGate weight",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
    }

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta column
    experiment_started = dataset.experiment_started
    df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

    # Convert types
    df = df.astype({
        "Animal": "category",
        "Direction": "category",
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
    dataset: Dataset,
    extension_data: dict[str, Datatable],
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

    tag_to_animal_map = get_tag_to_name_map(dataset.animals)

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

        for row in extension_data["Sessions"].df.itertuples():
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
        variables_csv_data = get_variables_csv_data(extension_data, EXTENSION_NAME, tag_to_animal_map)
        result.update(variables_csv_data)

    return EXTENSION_NAME, result
