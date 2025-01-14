from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.consumption_scale.data.consumption_scale_data import ConsumptionScaleData
from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset


def import_consumptionscale_data(
    folder_path: Path,
    im_dataset: IMDataset,
) -> ConsumptionScaleData | None:
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    consumption_df = _import_consumption_df(folder_path)
    model_df = _import_model_df(folder_path)

    data = ConsumptionScaleData(
        im_dataset,
        "ConsumptionScale",
        consumption_df,
        model_df,
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
