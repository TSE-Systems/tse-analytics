from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.modules.intellimaze.extensions.intellicage.data.intellicage_data import IntelliCageData
from tse_analytics.modules.intellimaze.io.variable_data_loader import import_variable_data
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


def import_data(
    folder_path: Path,
    dataset: IntelliMazeDataset,
) -> IntelliCageData:
    raw_data = {
        "Visits": _import_visits_df(folder_path),
        "Nosepokes": _import_nosepokes_df(folder_path),
        "Environment": _import_environment_df(folder_path),
        "HardwareEvents": _import_hardware_events_df(folder_path),
        "Log": _import_log_df(folder_path),
    }

    variables_data = import_variable_data(folder_path)
    if len(variables_data) > 0:
        raw_data = raw_data | variables_data

    data = IntelliCageData(
        dataset,
        "IntelliCage extension data",
        raw_data,
    )

    data.preprocess_data()

    return data


def _import_visits_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Visit.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "VisitID": np.int64,
        "AnimalTag": str,
        "Start": str,
        "End": str,
        "ModuleName": str,
        "DeviceId": str,
        "Corner": np.int8,
        "CornerCondition": np.int8,
        "PlaceError": bool,
        "AntennaNumber": np.int64,
        "AntennaDuration": np.float64,
        "PresenceNumber": np.int64,
        "PresenceDuration": np.float64,
        "VisitSolution": np.int8,
        "LickNumber": np.int64,
        "LickContactTime": np.float64,
        "LickDuration": np.float64,
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
    ).dt.tz_localize(None)

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

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
    df["VisitNumber"] = df.groupby("AnimalTag").cumcount().astype(np.int64)
    # df["VisitNumber"] = df.groupby("AnimalTag")["VisitID"].rank(method="first").astype(np.int64)

    return df


def _import_nosepokes_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Nosepoke.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "VisitID": np.int64,
        "Start": str,
        "End": str,
        "Side": np.int8,
        "SideCondition": np.int8,
        "SideError": bool,
        "TimeError": bool,
        "ConditionError": bool,
        "LickNumber": np.int64,
        "LickContactTime": np.float64,
        "LickDuration": np.float64,
        "AirState": bool,
        "DoorState": bool,
        "LED1State": np.int8,
        "LED2State": np.int8,
        "LED3State": np.int8,
        "LickStartTime": str,
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
    ).dt.tz_localize(None)

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    df["LickStartTime"] = pd.to_datetime(
        df["LickStartTime"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

    # Convert numeric Enum values to categories
    df["SideCondition"] = pd.Categorical(df["SideCondition"], categories=[-1, 0, 1], ordered=True)
    df["SideCondition"] = df["SideCondition"].cat.rename_categories({
        -1: "Incorrect",
        0: "Neutral",
        1: "Correct",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_environment_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Environment.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DateTimeOffset": str,
        "Temperature": np.float32,
        "Illumination": np.uint32,
        "DeviceId": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = pd.to_datetime(
        df["DateTimeOffset"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

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

    return df


def _import_hardware_events_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Hardware.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DateTimeOffset": str,
        "HardwareType": np.int8,
        "DeviceId": str,
        "Corner": np.int8,
        "Side": "Int8",
        "State": np.int32,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = pd.to_datetime(
        df["DateTimeOffset"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

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

    return df


def _import_log_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Log.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DateTimeOffset": str,
        "LogCategory": str,
        "LogType": str,
        "DeviceId": str,
        "Corner": "Int8",
        "Side": "Int8",
        "LogNotes": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Convert DateTime columns
    df["DateTimeOffset"] = pd.to_datetime(
        df["DateTimeOffset"],
        format="ISO8601",
        utc=False,
    ).dt.tz_localize(None)

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

    return df
