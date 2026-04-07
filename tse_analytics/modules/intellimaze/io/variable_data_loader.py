from pathlib import Path

import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT


def import_variable_data(dataset: Dataset, folder_path: Path) -> dict[str, Datatable]:
    """
    Import variable data from a folder.

    This function imports integer, double, and boolean variable data from a folder
    and returns a dictionary mapping variable types to DataFrames.

    Args:
        folder_path (Path): The path to the folder containing variable data.

    Returns:
        dict[str, pd.DataFrame]: Dictionary mapping variable types to DataFrames.
    """
    result: dict[str, Datatable] = {}

    integer_variables = _import_integer_variables_data(dataset, folder_path / "IntegerVariables.txt")
    if integer_variables is not None:
        result["IntegerVariables"] = integer_variables

    double_variables = _import_double_variables_data(dataset, folder_path / "DoubleVariables.txt")
    if double_variables is not None:
        result["DoubleVariables"] = double_variables

    boolean_variables = _import_boolean_variables_data(dataset, folder_path / "BooleanVariables.txt")
    if boolean_variables is not None:
        result["BooleanVariables"] = boolean_variables

    return result


def _import_integer_variables_data(dataset: Dataset, file_path: Path) -> Datatable | None:
    """
    Import integer variable data from a text file.

    This function reads a tab-delimited text file containing integer variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing integer variable data, or None if the file doesn't exist.
    """
    if not file_path.is_file():
        return None

    dtype = {
        "Time": "string",
        "DeviceId": "string",
        "Name": "string",
        "Data": "Int64",
        "ConditionValue": "Int64",
        "Tag": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["Time"] = (
        pd
        .to_datetime(
            df["Time"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    datatable = Datatable(
        dataset,
        "IntegerVariables",
        "IntelliMaze integer variables data",
        {},
        df,
        {},
    )

    return datatable


def _import_double_variables_data(dataset: Dataset, file_path: Path) -> Datatable | None:
    """
    Import double variable data from a text file.

    This function reads a tab-delimited text file containing double variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing double variable data, or None if the file doesn't exist.
    """
    if not file_path.is_file():
        return None

    dtype = {
        "Time": "string",
        "DeviceId": "string",
        "Name": "string",
        "Data": "Float64",
        "ConditionValue": "Float64",
        "Tag": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["Time"] = (
        pd
        .to_datetime(
            df["Time"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    datatable = Datatable(
        dataset,
        "DoubleVariables",
        "IntelliMaze double variables data",
        {},
        df,
        {},
    )

    return datatable


def _import_boolean_variables_data(dataset: Dataset, file_path: Path) -> Datatable | None:
    """
    Import boolean variable data from a text file.

    This function reads a tab-delimited text file containing boolean variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing boolean variable data, or None if the file doesn't exist.
    """
    if not file_path.is_file():
        return None

    dtype = {
        "Time": "string",
        "DeviceId": "string",
        "Name": "string",
        "Data": "boolean",
        "Tag": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["Time"] = (
        pd
        .to_datetime(
            df["Time"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    datatable = Datatable(
        dataset,
        "BooleanVariables",
        "IntelliMaze boolean variables data",
        {},
        df,
        {},
    )

    return datatable
