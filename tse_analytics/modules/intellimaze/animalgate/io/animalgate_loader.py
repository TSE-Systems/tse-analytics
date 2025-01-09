from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.animalgate.data.animalgate_data import AnimalGateData
from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset


def load_animalgate_data(
    folder_path: Path,
    im_dataset: IMDataset,
) -> AnimalGateData | None:
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    sessions_df = _load_sessions_df(folder_path)
    antenna_df = _load_antenna_df(folder_path)
    log_df = _load_log_df(folder_path)
    input_df = _load_input_df(folder_path)
    output_df = _load_output_df(folder_path)

    animalgate_data = AnimalGateData(
        im_dataset,
        "AnimalGate",
        sessions_df,
        antenna_df,
        log_df,
        input_df,
        output_df,
    )
    return animalgate_data


def _load_sessions_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Sessions.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DeviceId": str,
        "IdSectionVisited": bool,
        "StandbySectionVisited": bool,
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

    # Convert DateTime columns
    df["Start"] = pd.to_datetime(
        df["Start"],
        format="ISO8601",
        utc=False,
    )

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "Direction": "category",
        # "Tag": "category",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _load_antenna_df(folder_path: Path) -> pd.DataFrame | None:
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
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        # "Tag": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _load_log_df(folder_path: Path) -> pd.DataFrame | None:
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

    return df


def _load_input_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Input.txt"
    if not file_path.is_file():
        return None

    df = pd.read_csv(
        file_path,
        header=None,
    )

    return df


def _load_output_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Output.txt"
    if not file_path.is_file():
        return None

    df = pd.read_csv(
        file_path,
        header=None,
    )

    return df
