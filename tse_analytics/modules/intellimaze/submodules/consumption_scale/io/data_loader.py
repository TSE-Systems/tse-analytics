from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data
from tse_analytics.modules.intellimaze.submodules.consumption_scale.data.consumption_scale_data import (
    ConsumptionScaleData,
)
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


def import_consumptionscale_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> ConsumptionScaleData | None:
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    raw_data = {
        "Consumption": _import_consumption_df(folder_path),
        "Model": _import_model_df(folder_path),
    }

    variables_data = import_variable_data(folder_path)
    if len(variables_data) > 0:
        raw_data = raw_data | variables_data

    data = ConsumptionScaleData(
        dataset,
        "ConsumptionScale raw data",
        raw_data,
    )
    return data


def _import_consumption_df(folder_path: Path) -> pd.DataFrame | None:
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
