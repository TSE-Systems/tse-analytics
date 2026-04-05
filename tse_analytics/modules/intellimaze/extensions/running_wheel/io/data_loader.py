from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.extensions.running_wheel.data import processor
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: Dataset,
) -> dict[str, Datatable]:
    extension_data = {
        "Registration": _import_registration_df(dataset, folder_path / "Registration.txt"),
        "Model": _import_model_df(dataset, folder_path / "Model.txt"),
    }

    variables_data = import_variable_data(dataset, folder_path)
    if len(variables_data) > 0:
        extension_data = extension_data | variables_data

    processor.preprocess_data(dataset, extension_data)

    return extension_data


def _import_registration_df(dataset: Dataset, file_path: Path) -> Datatable:
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

    datatable = Datatable(
        dataset,
        "Registration",
        f"{processor.EXTENSION_NAME} registration data",
        {},
        df,
        {},
    )

    return datatable


def _import_model_df(dataset: Dataset, file_path: Path) -> Datatable:
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

    datatable = Datatable(
        dataset,
        "Model",
        f"{processor.EXTENSION_NAME} model data",
        {},
        df,
        {},
    )

    return datatable
