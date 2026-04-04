from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.extensions.running_wheel.data.running_wheel_data import RunningWheelData
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> RunningWheelData:
    raw_data = {
        "Registration": _import_registration_df(folder_path),
        "Model": _import_model_df(folder_path),
    }

    variables_data = import_variable_data(folder_path)
    if len(variables_data) > 0:
        raw_data = raw_data | variables_data

    data = RunningWheelData(
        dataset,
        "RunningWheel extension data",
        raw_data,
    )

    data.preprocess_data()

    return data


def _import_registration_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Registration.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Registration file not found: {file_path}")

    dtype = {
        "Time": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Left": "int64[pyarrow]",
        "Right": "int64[pyarrow]",
        "Reset": "bool[pyarrow]",
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
    })

    df.sort_values(["Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    return df


def _import_model_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Model.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Model file not found: {file_path}")

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
