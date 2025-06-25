"""
Data loader for Consumption Scale extension.

This module provides functions for importing Consumption Scale data from files.
It includes functions for loading consumption and model data, as well as variable data.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data
from tse_analytics.modules.intellimaze.extensions.consumption_scale.data.consumption_scale_data import (
    ConsumptionScaleData,
)
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


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


def _import_consumption_df(folder_path: Path) -> pd.DataFrame | None:
    """
    Import consumption data from a file.

    This function loads data from the Consumption.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the Consumption.txt file.

    Returns:
        pd.DataFrame | None: A DataFrame containing the consumption data, or None if the file doesn't exist.
    """
    file_path = folder_path / "Consumption.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Consumption": np.float64,
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


def _import_model_df(folder_path: Path) -> pd.DataFrame | None:
    """
    Import model data from a file.

    This function loads data from the Model.txt file in the specified folder,
    performs type conversions, and sorts the data by time.

    Args:
        folder_path (Path): Path to the folder containing the Model.txt file.

    Returns:
        pd.DataFrame | None: A DataFrame containing the model data, or None if the file doesn't exist.
    """
    file_path = folder_path / "Model.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "SwitchMode": str,
        "Model": str,
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
        "SwitchMode": "category",
        "Model": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
