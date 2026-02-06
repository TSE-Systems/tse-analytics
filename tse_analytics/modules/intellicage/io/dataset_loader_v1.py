"""
IntelliCage Dataset Loader for Version 1 Format.

This module provides functions for loading IntelliCage datasets in version 1 format.
It includes functions for importing metadata, animals, visits, nosepokes, environment data,
hardware events, and logs from the extracted dataset files.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xmltodict

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset


def import_intellicage_dataset_v1(path: Path, tmp_path: Path, data_descriptor: dict) -> IntelliCageDataset | None:
    """
    Imports older IntelliCage datasets with DataVersion 1.x.
    """
    metadata = _import_metadata(tmp_path / "Sessions.xml")
    animals = _import_animals(tmp_path / "Animals.txt")

    dataset = IntelliCageDataset(
        metadata={
            "name": path.stem,
            "description": "IntelliCage dataset v1",
            "source_path": str(path),
            "experiment_started": metadata["Interval"]["Start"],
            "experiment_stopped": metadata["Interval"]["End"],
            "data_descriptor": data_descriptor,
            "experiment": metadata,
            "animals": {k: v.get_dict() for (k, v) in animals.items()},
        },
        animals=animals,
    )

    raw_data = {
        "Visits": _import_visits_df(tmp_path),
        "Nosepokes": _import_nosepokes_df(tmp_path),
        "Environment": _import_environment_df(tmp_path),
        "HardwareEvents": _import_hardware_events_df(tmp_path),
        "Log": _import_log_df(tmp_path),
    }

    dataset.intellicage_data = IntelliCageData(
        dataset,
        "IntelliCage raw data",
        raw_data,
    )

    dataset.intellicage_data.preprocess_data()

    return dataset


def _import_metadata(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["ArrayOfSession"]["Session"]


def _import_animals(path: Path) -> dict | None:
    if not path.is_file():
        return None

    dtype = {
        "Name": str,
        "Tag": str,
        "Sex": str,
        "Group": str,
        "Notes": str,
    }

    df = pd.read_csv(
        path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Replace np.nan with empty strings
    df.fillna({"Notes": ""}, inplace=True)

    animals = {}
    index = 0
    for _, row in df.iterrows():
        properties = {
            "Tag": row["Tag"],
            "Sex": row["Sex"],
            "Group": row["Group"],
            "Notes": row["Notes"],
        }
        animal = Animal(
            enabled=True,
            id=str(row["Name"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
        index += 1

    # Sort animals by ID
    animals = dict(sorted(animals.items()))

    return animals


def _import_visits_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Visits.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "ID": np.int64,
        "Animal": str,
        "Start": str,
        "End": str,
        "Module": str,
        "Cage": np.int8,
        "Corner": np.int8,
        "CornerCondition": np.int8,
        "PlaceError": bool,
        "AntennaNumber": np.int64,
        "AntennaDuration": np.float64,
        "PresenceNumber": np.int64,
        "PresenceDuration": np.float64,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Standardize column names across different versions
    df.rename(
        columns={
            "ID": "VisitID",
            "Animal": "AnimalTag",
            "Module": "ModuleName",
        },
        inplace=True,
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

    # Convert numeric Enum values to categories
    df = df.astype({
        "ModuleName": "category",
    })

    df["CornerCondition"] = pd.Categorical(df["CornerCondition"], categories=[-1, 0, 1], ordered=True)
    df["CornerCondition"] = df["CornerCondition"].cat.rename_categories({
        -1: "Incorrect",
        0: "Neutral",
        1: "Correct",
    })

    df.sort_values(["Start"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Set visit number column
    df["VisitNumber"] = df.groupby("AnimalTag").cumcount().astype(np.int64)
    # df["VisitNumber"] = df.groupby("AnimalTag")["VisitID"].rank(method="first").astype(np.int64)

    return df


def _import_nosepokes_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Nosepokes.txt"
    if not file_path.is_file():
        return None

    # with open(file_path) as file:
    #     first_line = file.readline()

    dtype = {
        "VisitID": np.int64,
        "Start": str,
        "End": str,
        "Side": np.int8,
        "SideCondition": np.int8,
        "SideError": bool,
        "TimeError": bool,
        "ConditionError": bool,
        "LicksNumber": np.int64,
        "LicksDuration": np.float64,
        "AirState": bool,
        "DoorState": bool,
        "LED1State": np.int8,
        "LED2State": np.int8,
        "LED3State": np.int8,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Standardize column names across different versions
    df.rename(
        columns={
            "LicksNumber": "LickNumber",
            "LicksDuration": "LickDuration",
        },
        inplace=True,
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
        "DateTime": str,
        "Temperature": np.float64,
        "Illumination": np.int64,
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

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_hardware_events_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "HardwareEvents.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "DateTime": str,
        "Type": np.int8,
        "Cage": np.int8,
        "Corner": np.int8,
        "Side": "Int64",
        "State": np.int8,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Standardize column names across different versions
    df.rename(
        columns={
            "Type": "HardwareType",
        },
        inplace=True,
    )

    # Convert DateTime columns
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    )

    # Convert numeric Enum values to categories
    df["HardwareType"] = df["HardwareType"].astype("category")
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
        "DateTime": str,
        "Category": str,
        "Type": str,
        "Cage": "Int64",
        "Corner": "Int64",
        "Side": "Int64",
        "Notes": str,
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Standardize column names across different versions
    df.rename(
        columns={
            "Category": "LogCategory",
            "Type": "LogType",
            "Notes": "LogNotes",
        },
        inplace=True,
    )

    # Convert DateTime columns
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "LogCategory": "category",
        "LogType": "category",
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
