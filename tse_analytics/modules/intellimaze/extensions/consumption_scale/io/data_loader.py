"""
Data loader for Consumption Scale extension.

This module provides functions for importing Consumption Scale data from files.
It includes functions for loading consumption and model data, as well as variable data.
"""

from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.extensions.consumption_scale.data.consumption_scale_data import (
    ConsumptionScaleData,
)
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> ConsumptionScaleData:
    """
    Import Consumption Scale data from files.

    This function loads data from various files in the specified folder,
    creates a ConsumptionScaleData object, and preprocesses the data.

    Args:
        folder_path (Path): Path to the folder containing the data files.
        dataset (IntelliMazeDataset): The dataset to add the data to.

    Returns:
        ConsumptionScaleData: A ConsumptionScaleData object containing the imported data.
    """
    raw_data = {
        "Consumption": _import_consumption_df(folder_path),
        "Model": _import_model_df(folder_path),
    }

    variables_data = import_variable_data(folder_path)
    if len(variables_data) > 0:
        raw_data = raw_data | variables_data

    data = ConsumptionScaleData(
        dataset,
        "ConsumptionScale extension data",
        raw_data,
    )

    data.preprocess_data()

    return data


def _import_consumption_df(folder_path: Path) -> pd.DataFrame:
    """
    Import consumption data from a file.

    This function loads data from the Consumption.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the Consumption.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the consumption data.
    """
    file_path = folder_path / "Consumption.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    dtype = {
        "Time": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Consumption": "float64[pyarrow]",
        "Tag": "string[pyarrow]",
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

    return df


def _import_model_df(folder_path: Path) -> pd.DataFrame:
    """
    Import model data from a file.

    This function loads data from the Model.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the Model.txt file.

    Returns:
        pd.DataFrame: A DataFrame containing the model data.
    """
    file_path = folder_path / "Model.txt"
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

    return df
