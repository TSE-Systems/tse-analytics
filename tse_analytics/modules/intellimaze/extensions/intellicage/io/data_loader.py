from pathlib import Path

import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.extensions.intellicage.data import processor
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data


def import_data(
    folder_path: Path,
    dataset: Dataset,
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


def _import_visits_df(dataset: Dataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Visit file not found: {file_path}")

    dtype = {
        "VisitID": "UInt64",
        "AnimalTag": "string",
        "Start": "string",
        "End": "string",
        "ModuleName": "string",
        "DeviceId": "string",
        "Corner": "UInt8",
        "CornerCondition": "Int8",
        "PlaceError": "boolean",
        "AntennaNumber": "UInt64",
        "AntennaDuration": "Float64",
        "PresenceNumber": "UInt64",
        "PresenceDuration": "Float64",
        "VisitSolution": "UInt8",
        "LickNumber": "UInt64",
        "LickContactTime": "Float64",
        "LickDuration": "Float64",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
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
    df["VisitNumber"] = df.groupby("AnimalTag").cumcount().astype("UInt64")
    # df["VisitNumber"] = df.groupby("AnimalTag")["VisitID"].rank(method="first").astype("UInt64")

    datatable = Datatable(
        dataset,
        "Visits",
        f"{processor.EXTENSION_NAME} visits data",
        {},
        df,
        {},
    )

    return datatable


def _import_nosepokes_df(dataset: Dataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Nosepoke file not found: {file_path}")

    dtype = {
        "VisitID": "UInt64",
        "Start": "string",
        "End": "string",
        "Side": "UInt8",
        "SideCondition": "Int8",
        "SideError": "boolean",
        "TimeError": "boolean",
        "ConditionError": "boolean",
        "LickNumber": "UInt64",
        "LickContactTime": "Float64",
        "LickDuration": "Float64",
        "AirState": "boolean",
        "DoorState": "boolean",
        "LED1State": "UInt8",
        "LED2State": "UInt8",
        "LED3State": "UInt8",
        "LickStartTime": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
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

    datatable = Datatable(
        dataset,
        "Nosepokes",
        f"{processor.EXTENSION_NAME} nosepokes data",
        {},
        df,
        {},
    )

    return datatable


def _import_environment_df(dataset: Dataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Environment file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string",
        "Temperature": "Float32",
        "Illumination": "UInt32",
        "DeviceId": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
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

    datatable = Datatable(
        dataset,
        "Environment",
        f"{processor.EXTENSION_NAME} environment data",
        {},
        df,
        {},
    )

    return datatable


def _import_hardware_events_df(dataset: Dataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Hardware events file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string",
        "HardwareType": "UInt8",
        "DeviceId": "string",
        "Corner": "UInt8",
        "Side": "UInt8",
        "State": "UInt32",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
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

    datatable = Datatable(
        dataset,
        "HardwareEvents",
        f"{processor.EXTENSION_NAME} hardware events data",
        {},
        df,
        {},
    )

    return datatable


def _import_log_df(dataset: Dataset, file_path: Path) -> Datatable:
    if not file_path.is_file():
        raise FileNotFoundError(f"Log file not found: {file_path}")

    dtype = {
        "DateTimeOffset": "string",
        "LogCategory": "string",
        "LogType": "string",
        "DeviceId": "string",
        "Corner": "UInt8",
        "Side": "UInt8",
        "LogNotes": "string",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
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

    datatable = Datatable(
        dataset,
        "Log",
        f"{processor.EXTENSION_NAME} log data",
        {},
        df,
        {},
    )

    return datatable
