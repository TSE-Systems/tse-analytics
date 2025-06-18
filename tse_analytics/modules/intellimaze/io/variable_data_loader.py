from pathlib import Path

import pandas as pd


def import_variable_data(folder_path: Path) -> dict[str, pd.DataFrame]:
    """
    Import variable data from a folder.

    This function imports integer, double, and boolean variable data from a folder
    and returns a dictionary mapping variable types to DataFrames.

    Args:
        folder_path (Path): The path to the folder containing variable data.

    Returns:
        dict[str, pd.DataFrame]: Dictionary mapping variable types to DataFrames.
    """
    result = {}

    integer_variables = _import_integer_variables_data(folder_path)
    if integer_variables is not None:
        result["IntegerVariables"] = integer_variables

    double_variables = _import_double_variables_data(folder_path)
    if double_variables is not None:
        result["DoubleVariables"] = double_variables

    boolean_variables = _import_boolean_variables_data(folder_path)
    if boolean_variables is not None:
        result["BooleanVariables"] = boolean_variables

    return result


def _import_integer_variables_data(folder_path: Path) -> pd.DataFrame | None:
    """
    Import integer variable data from a text file.

    This function reads a tab-delimited text file containing integer variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing integer variable data, or None if the file doesn't exist.
    """
    file_path = folder_path / "IntegerVariables.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Name": str,
        "Data": int,
        "ConditionValue": int,
        "Tag": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["Time"] = pd.to_datetime(
        df["Time"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_double_variables_data(folder_path: Path) -> pd.DataFrame | None:
    """
    Import double variable data from a text file.

    This function reads a tab-delimited text file containing double variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing double variable data, or None if the file doesn't exist.
    """
    file_path = folder_path / "DoubleVariables.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Name": str,
        "Data": float,
        "ConditionValue": float,
        "Tag": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["Time"] = pd.to_datetime(
        df["Time"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_boolean_variables_data(folder_path: Path) -> pd.DataFrame | None:
    """
    Import boolean variable data from a text file.

    This function reads a tab-delimited text file containing boolean variable data,
    converts data types, and returns a DataFrame.

    Args:
        folder_path (Path): The path to the folder containing the text file.

    Returns:
        pd.DataFrame | None: DataFrame containing boolean variable data, or None if the file doesn't exist.
    """
    file_path = folder_path / "BooleanVariables.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Name": str,
        "Data": bool,
        "Tag": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["Time"] = pd.to_datetime(
        df["Time"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
