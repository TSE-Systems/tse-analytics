from pathlib import Path

import pandas as pd


def import_variable_data(folder_path: Path) -> dict[str, pd.DataFrame]:
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
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_double_variables_data(folder_path: Path) -> pd.DataFrame | None:
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
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_boolean_variables_data(folder_path: Path) -> pd.DataFrame | None:
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
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
