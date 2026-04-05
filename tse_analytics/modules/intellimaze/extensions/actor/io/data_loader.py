"""
Data loader for Actor extension.

This module provides functions for importing Actor data from files.
It includes functions for loading state and model data, as well as variable data.
"""

from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.extensions.actor.data import processor
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: Dataset,
) -> dict[str, Datatable]:
    """
    Import Actor data from files.

    This function loads data from various files in the specified folder,
    creates an ActorData object, and preprocesses the data.

    Args:
        folder_path (Path): Path to the folder containing the data files.
        dataset (Dataset): The dataset to add the data to.
    """
    extension_data = {
        "State": _import_state_df(dataset, folder_path / "State.txt"),
        "Model": _import_model_df(dataset, folder_path / "Model.txt"),
    }

    variables_data = import_variable_data(dataset, folder_path)
    if len(variables_data) > 0:
        extension_data = extension_data | variables_data

    processor.preprocess_data(dataset, extension_data)

    return extension_data


def _import_state_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    """
    Import state data from a file.

    This function loads data from the State.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the State.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the state data.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "Time": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Mode": "string[pyarrow]",
        "State": "string[pyarrow]",
        "AnimalTag": "string[pyarrow]",
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
        "Mode": "category",
        "State": "category",
        # "AnimalTag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "State",
        f"{processor.EXTENSION_NAME} state data",
        {},
        df,
        {},
    )

    return datatable


def _import_model_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "Time": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "SwitchMode": "string[pyarrow]",
        "Model": "string[pyarrow]",
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
        "SwitchMode": "category",
        "Model": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Model",
        f"{processor.EXTENSION_NAME} model data",
        {},
        df,
        {},
    )

    return datatable
