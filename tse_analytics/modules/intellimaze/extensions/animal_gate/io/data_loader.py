"""
Data loader for Animal Gate extension.

This module provides functions for importing Animal Gate data from files.
It includes functions for loading sessions, antenna, log, input, and output data,
as well as variable data.
"""

from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.extensions.animal_gate.data import processor
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> dict[str, Datatable]:
    """
    Import Animal Gate data from files.

    This function loads data from various files in the specified folder,
    creates an AnimalGateData object, and preprocesses the data.

    Args:
        folder_path (Path): Path to the folder containing the data files.
        dataset (IntelliMazeDataset): The dataset to add the data to.
    """
    extension_data = {
        "Sessions": _import_sessions_df(dataset, folder_path / "Sessions.txt"),
        "Antenna": _import_antenna_df(dataset, folder_path / "Antenna.txt"),
        "Log": _import_log_df(dataset, folder_path / "Log.txt"),
        "Input": _import_input_df(dataset, folder_path / "Input.txt"),
        "Output": _import_output_df(dataset, folder_path / "Output.txt"),
    }

    variables_data = import_variable_data(dataset, folder_path)
    if len(variables_data) > 0:
        extension_data = extension_data | variables_data

    processor.preprocess_data(dataset, extension_data)

    return extension_data


def _import_sessions_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import sessions data from a file.

    This function loads data from the Sessions.txt file in the specified folder,
    performs type conversions, and sorts the data by start time.

    Args:
        folder_path (Path): Path to the folder containing the Sessions.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the sessions data.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "DeviceId": "string[pyarrow]",
        "IdSectionVisited": "uint8[pyarrow]",
        "StandbySectionVisited": "uint8[pyarrow]",
        "Direction": "string[pyarrow]",
        "Weight": "float64[pyarrow]",
        "Tag": "string[pyarrow]",
        "Start": "string[pyarrow]",
        "End": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # TODO: does -1 means no weight measurement?
    df["Weight"] = df["Weight"].replace(-1, pd.NA)

    # Convert DateTime columns
    df["Start"] = (
        pd
        .to_datetime(
            df["Start"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    df["End"] = (
        pd
        .to_datetime(
            df["End"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "Direction": "category",
        # "Tag": "category",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Sessions",
        f"{processor.EXTENSION_NAME} sessions data",
        {},
        df,
        {},
    )

    return datatable


def _import_antenna_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import antenna data from a file.

    This function loads data from the Antenna.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the Antenna.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the antenna data.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "Time": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Tag": "string[pyarrow]",
        "AnimalName": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
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
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Antenna",
        f"{processor.EXTENSION_NAME} antenna data",
        {},
        df,
        {},
    )

    return datatable


def _import_log_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import log data from a file.

    This function loads data from the Log.txt file in the specified folder,
    performs type conversions, and sorts the data by datetime.

    Args:
        folder_path (Path): Path to the folder containing the Log.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the log data.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "DateTime": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Phase": "string[pyarrow]",
        "Flag": "string[pyarrow]",
        "Tag": "string[pyarrow]",
        "Description": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["DateTime"] = (
        pd
        .to_datetime(
            df["DateTime"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "Phase": "category",
        "Flag": "category",
        # "Tag": "category",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Log",
        f"{processor.EXTENSION_NAME} log data",
        {},
        df,
        {},
    )

    return datatable


def _import_input_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import input data from a file.

    This function loads data from the Input.txt file in the specified folder.

    Args:
        folder_path (Path): Path to the folder containing the Input.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the input data.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(
        file_path,
        header=None,
        dtype_backend="pyarrow",
    )

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Input",
        f"{processor.EXTENSION_NAME} input data",
        {},
        df,
        {},
    )

    return datatable


def _import_output_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import output data from a file.

    This function loads data from the Output.txt file in the specified folder.

    Args:
        folder_path (Path): Path to the folder containing the Output.txt file.

    Returns:
        pd.DataFrame | None: A DataFrame containing the output data, or None if the file doesn't exist.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(
        file_path,
        header=None,
        dtype_backend="pyarrow",
    )

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Output",
        f"{processor.EXTENSION_NAME} output data",
        {},
        df,
        {},
    )

    return datatable
