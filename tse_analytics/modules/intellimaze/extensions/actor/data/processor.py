import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.utils import (
    get_combined_variables_table,
    get_tag_to_name_map,
    get_variables_csv_data,
)

EXTENSION_NAME = "Actor"


def preprocess_data(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
) -> None:
    df = extension_data["State"].df.copy()

    # Replace animal tags with animal IDs
    tag_to_animal_map = get_tag_to_name_map(dataset.animals)
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
            "string",
            Aggregation.SUM,
            False,
        ),
        "State": Variable(
            "State",
            "category",
            "Actor state",
            "string",
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
    dataset: Dataset,
    extension_data: dict[str, Datatable],
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

    tag_to_animal_map = get_tag_to_name_map(dataset.animals)

    if export_registrations:
        # Skip actor state data
        pass

    if export_variables:
        variables_csv_data = get_variables_csv_data(extension_data, EXTENSION_NAME, tag_to_animal_map)
        result.update(variables_csv_data)

    return EXTENSION_NAME, result
