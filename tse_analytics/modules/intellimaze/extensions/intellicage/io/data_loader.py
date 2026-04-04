from pathlib import Path

import pandas as pd
import pyarrow as pa

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.extensions.intellicage.data import processor
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> dict[str, Datatable]:
    extension_data = {
        "Visits": _import_visits_df(dataset, folder_path / "Visit.txt"),
        "Nosepokes": _import_nosepokes_df(dataset, folder_path / "Nosepoke.txt"),
        "Environment": _import_environment_df(dataset, folder_path / "Environment.txt"),
        "HardwareEvents": _import_hardware_events_df(dataset, folder_path / "Hardware.txt"),
        "Log": _import_log_df(dataset, folder_path / "Log.txt"),
    }

    variables_data = import_variable_data(dataset, folder_path)
    if len(variables_data) > 0:
        extension_data = extension_data | variables_data

    processor.preprocess_data(dataset, extension_data)

    return extension_data


def _import_visits_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Visit file not found: {file_path}")

    dtype = {
        "VisitID": "uint64[pyarrow]",
        "AnimalTag": "string[pyarrow]",
        "Start": "string[pyarrow]",
        "End": "string[pyarrow]",
        "ModuleName": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Corner": "uint8",
        "CornerCondition": "int8[pyarrow]",
        "PlaceError": "bool[pyarrow]",
        "AntennaNumber": "uint64[pyarrow]",
        "AntennaDuration": "float64[pyarrow]",
        "PresenceNumber": "uint64[pyarrow]",
        "PresenceDuration": "float64[pyarrow]",
        "VisitSolution": "uint8[pyarrow]",
        "LickNumber": "uint64[pyarrow]",
        "LickContactTime": "float64[pyarrow]",
        "LickDuration": "float64[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["Start"] = (
        pd
        .to_datetime(
            df["Start"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    df["End"] = (
        pd
        .to_datetime(
            df["End"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "DeviceId": "category",
        "ModuleName": "category",
    })

    df["CornerCondition"] = pd.Categorical(df["CornerCondition"], categories=[-1, 0, 1], ordered=True)
    df["CornerCondition"] = df["CornerCondition"].cat.rename_categories({
        -1: "Incorrect",
        0: "Neutral",
        1: "Correct",
    })

    df["VisitSolution"] = pd.Categorical(df["VisitSolution"], categories=[0, 1, 2, 3, 4], ordered=True)
    df["VisitSolution"] = df["VisitSolution"].cat.rename_categories({
        0: "Standard",
        1: "AnotherCorner",
        2: "AnotherAnimal",
        3: "AnotherAnimalPresenceOn",
        4: "AnotherAnimalPresenceOff",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Set visit number column
    df["VisitNumber"] = df.groupby("AnimalTag").cumcount().astype("uint64[pyarrow]")
    # df["VisitNumber"] = df.groupby("AnimalTag")["VisitID"].rank(method="first").astype("UInt64")

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Visits",
        f"{processor.EXTENSION_NAME} visits data",
        {},
        df,
        {},
    )

    return datatable


def _import_nosepokes_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Nosepoke file not found: {file_path}")

    dtype = {
        "VisitID": "uint64[pyarrow]",
        "Start": "string[pyarrow]",
        "End": "string[pyarrow]",
        "Side": "uint8[pyarrow]",
        "SideCondition": "int8[pyarrow]",
        "SideError": "bool[pyarrow]",
        "TimeError": "bool[pyarrow]",
        "ConditionError": "bool[pyarrow]",
        "LickNumber": "uint64[pyarrow]",
        "LickContactTime": "float64[pyarrow]",
        "LickDuration": "float64[pyarrow]",
        "AirState": "bool[pyarrow]",
        "DoorState": "bool[pyarrow]",
        "LED1State": "uint8[pyarrow]",
        "LED2State": "uint8[pyarrow]",
        "LED3State": "uint8[pyarrow]",
        "LickStartTime": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["Start"] = (
        pd
        .to_datetime(
            df["Start"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    df["End"] = (
        pd
        .to_datetime(
            df["End"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    df["LickStartTime"] = (
        pd
        .to_datetime(
            df["LickStartTime"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Convert numeric Enum values to categories
    df["SideCondition"] = pd.Categorical(df["SideCondition"], categories=[-1, 0, 1], ordered=True)
    df["SideCondition"] = df["SideCondition"].cat.rename_categories({
        -1: "Incorrect",
        0: "Neutral",
        1: "Correct",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Nosepokes",
        f"{processor.EXTENSION_NAME} nosepokes data",
        {},
        df,
        {},
    )

    return datatable


def _import_environment_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Environment file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string[pyarrow]",
        "Temperature": "float32[pyarrow]",
        "Illumination": "uint32[pyarrow]",
        "DeviceId": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = (
        pd
        .to_datetime(
            df["DateTimeOffset"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Standardize column names
    df.rename(
        columns={
            "DateTimeOffset": "DateTime",
        },
        inplace=True,
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "DeviceId": "category",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Environment",
        f"{processor.EXTENSION_NAME} environment data",
        {},
        df,
        {},
    )

    return datatable


def _import_hardware_events_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Hardware events file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string[pyarrow]",
        "HardwareType": "uint8[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Corner": "uint8[pyarrow]",
        "Side": "uint8[pyarrow]",
        "State": "uint32[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = (
        pd
        .to_datetime(
            df["DateTimeOffset"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Standardize column names
    df.rename(
        columns={
            "DateTimeOffset": "DateTime",
        },
        inplace=True,
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "HardwareType": "category",
        "DeviceId": "category",
    })
    df["HardwareType"] = df["HardwareType"].cat.rename_categories({
        0: "Air",
        1: "Door",
        2: "LED",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "HardwareEvents",
        f"{processor.EXTENSION_NAME} hardware events data",
        {},
        df,
        {},
    )

    return datatable


def _import_log_df(dataset: IntelliMazeDataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Log file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string[pyarrow]",
        "LogCategory": "string[pyarrow]",
        "LogType": "string[pyarrow]",
        "DeviceId": "string[pyarrow]",
        "Corner": "uint8[pyarrow]",
        "Side": "uint8[pyarrow]",
        "LogNotes": "string[pyarrow]",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="pyarrow",
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = (
        pd
        .to_datetime(
            df["DateTimeOffset"],
            format="ISO8601",
            utc=False,
        )
        .dt.tz_localize(None)
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Standardize column names
    df.rename(
        columns={
            "DateTimeOffset": "DateTime",
        },
        inplace=True,
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "LogCategory": "category",
        "LogType": "category",
        "DeviceId": "category",
    })

    df["LogCategory"] = df["LogCategory"].cat.rename_categories({
        0: "Info",
        1: "Warning",
        2: "Error",
    })

    df["LogType"] = df["LogType"].cat.rename_categories({
        0: "Application",
        1: "Animal",
        2: "Antenna",
        3: "Presence",
        4: "Nosepoke",
        5: "Lickometer",
        6: "Environment",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    datatable = Datatable(
        dataset,
        "Log",
        f"{processor.EXTENSION_NAME} log data",
        {},
        df,
        {},
    )

    return datatable
