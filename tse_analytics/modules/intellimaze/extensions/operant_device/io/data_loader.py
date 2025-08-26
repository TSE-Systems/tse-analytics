from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.extensions.operant_device.data.operant_device_data import OperantDeviceData
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> OperantDeviceData:
    raw_data = {
        "Sessions": _import_sessions_df(folder_path),
        "Antenna": _import_antenna_df(folder_path),
        "Log": _import_log_df(folder_path),
        "Input": _import_input_df(folder_path),
        "Output": _import_output_df(folder_path),
    }

    variables_data = import_variable_data(folder_path)
    if len(variables_data) > 0:
        raw_data = raw_data | variables_data

    data = OperantDeviceData(
        dataset,
        "OperantDevice extension data",
        raw_data,
    )

    data.preprocess_data()

    return data


def _import_sessions_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Sessions.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DeviceId": str,
        "IdSectionVisited": np.int8,
        "StandbySectionVisited": np.int8,
        "Direction": str,
        "Weight": np.float64,
        "Tag": str,
        "Start": str,
        "End": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # TODO: does -1 means no weight measurement?
    df["Weight"] = df["Weight"].replace(-1, np.nan)

    # Convert DateTime columns
    df["Start"] = pd.to_datetime(
        df["Start"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "Direction": "category",
        # "Tag": "category",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_antenna_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Antenna.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Tag": str,
        "AnimalName": str,
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


def _import_log_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Log.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DateTime": str,
        "DeviceId": str,
        "Phase": str,
        "Flag": str,
        "Tag": str,
        "Description": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "Phase": "category",
        "Flag": "category",
        # "Tag": "category",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_input_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Input.txt"
    if not file_path.is_file():
        return None

    df = pd.read_csv(
        file_path,
        header=None,
    )

    return df


def _import_output_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Output.txt"
    if not file_path.is_file():
        return None

    df = pd.read_csv(
        file_path,
        header=None,
    )

    return df
