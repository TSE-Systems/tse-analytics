from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset
from tse_analytics.modules.intellimaze.running_wheel.data.running_wheel_data import RunningWheelData


def import_runningwheel_data(
    folder_path: Path,
    im_dataset: IMDataset,
) -> RunningWheelData | None:
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    registration_df = _import_registration_df(folder_path)
    model_df = _import_model_df(folder_path)

    data = RunningWheelData(
        im_dataset,
        "RunningWheel",
        registration_df,
        model_df,
    )
    return data


def _import_registration_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Registration.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "Time": str,
        "DeviceId": str,
        "Left": np.int64,
        "Right": np.int64,
        "Reset": bool,
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


def _import_model_df(folder_path: Path) -> pd.DataFrame | None:
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
    )

    # Convert categorical types
    df = df.astype({
        "DeviceId": "category",
        "SwitchMode": "category",
        "Model": "category",
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
