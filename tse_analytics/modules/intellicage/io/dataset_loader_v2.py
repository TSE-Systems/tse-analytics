from dataclasses import asdict
from pathlib import Path

import pandas as pd
import xmltodict

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellicage.data.processor import get_nosepokes_datatable, get_visits_datatable


def import_intellicage_dataset_v2(path: Path, tmp_path: Path, data_descriptor: dict) -> Dataset | None:
    """
    Imports IntelliCage datasets with DataVersion 2.x.
    """
    metadata = _import_metadata(tmp_path / "Sessions.xml")
    animals = _import_animals(tmp_path / "Animals.txt")

    folder_path = tmp_path / "IntelliCage"
    raw_data = {
        "Visits": _import_visits_df(folder_path),
        "Nosepokes": _import_nosepokes_df(folder_path),
        "Environment": _import_environment_df(folder_path),
        "HardwareEvents": _import_hardware_events_df(folder_path),
        "Log": _import_log_df(folder_path),
    }

    dataset = Dataset(
        path.stem,
        "IntelliCage dataset v2",
        "IntelliCage",
        {
            "source_path": str(path),
            "experiment_started": metadata["Interval"]["Start"],
            "experiment_stopped": metadata["Interval"]["End"],
            "data_descriptor": data_descriptor,
            "experiment": metadata,
            "animals": {k: asdict(v) for (k, v) in animals.items()},
        },
        animals,
    )

    device_ids = raw_data["HardwareEvents"]["Cage"].unique().tolist()
    device_ids.sort()
    dataset.metadata["device_ids"] = device_ids

    for table_name, raw_df in raw_data.items():
        datatable = Datatable(
            dataset,
            table_name,
            f"IntelliCage [{table_name}]",
            {},
            raw_df,
            {},
        )
        dataset.add_raw_datatable("IntelliCage", datatable)

    visits_datatable = get_visits_datatable(dataset)
    dataset.add_datatable(visits_datatable)

    nosepokes_datatable = get_nosepokes_datatable(dataset, visits_datatable)
    dataset.add_datatable(nosepokes_datatable)

    return dataset


def _import_metadata(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Sessions file not found: {path}")

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["ArrayOfSession"]["Session"]


def _import_animals(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Animals file not found: {path}")

    dtype = {
        "AnimalName": "string",
        "AnimalTag": "string",
        "Sex": "string",
        "GroupName": "string",
        "AnimalNotes": "string",
    }

    # Skip broken header
    df = pd.read_csv(
        path,
        header=0,
        usecols=["AnimalName", "AnimalTag", "Sex", "GroupName", "AnimalNotes"],
        names=["AnimalName", "AnimalTag", "Sex", "GroupName", "AnimalNotes"],
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Replace np.nan with empty strings
    df.fillna({"AnimalNotes": ""}, inplace=True)

    animals = {}
    index = 0
    for _, row in df.iterrows():
        properties = {
            "Tag": row["AnimalTag"],
            "Sex": row["Sex"],
            "Group": row["GroupName"],
            "Notes": row["AnimalNotes"],
        }
        animal = Animal(
            id=str(row["AnimalName"]),
            properties=properties,
        )
        animals[animal.id] = animal
        index += 1

    # Sort animals by ID
    animals = dict(sorted(animals.items()))

    return animals


def _import_visits_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Visits.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Visits file not found: {file_path}")

    dtype = {
        "VisitID": "UInt64",
        "AnimalTag": "string",
        "Start": "string",
        "End": "string",
        "ModuleName": "string",
        "Cage": "UInt8",
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
    df["Start"] = pd.to_datetime(
        df["Start"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

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

    return df


def _import_nosepokes_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Nosepokes.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Nosepokes file not found: {file_path}")

    with open(file_path) as file:
        first_line = file.readline()
        lick_start_time_column = "LickStartTime" in first_line

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
    }

    if lick_start_time_column:
        dtype["LickStartTime"] = str

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["Start"] = pd.to_datetime(
        df["Start"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

    if lick_start_time_column:
        df["LickStartTime"] = pd.to_datetime(
            df["LickStartTime"],
            format="ISO8601",
            utc=False,
        ).dt.as_unit(TIME_RESOLUTION_UNIT)

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


def _import_environment_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Environment.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Environment file not found: {file_path}")

    dtype = {
        "DateTime": "string",
        "Temperature": "Float64",
        "Illumination": "UInt64",
        "Cage": "UInt8",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def _import_hardware_events_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "HardwareEvents.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"HardwareEvents file not found: {file_path}")

    dtype = {
        "DateTime": "string",
        "HardwareType": "UInt8",
        "Cage": "UInt8",
        "Corner": "UInt8",
        "Side": "UInt8",
        "State": "UInt8",
    }

    df = pd.read_csv(
        file_path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
        dtype_backend="numpy_nullable",
    )

    # Convert DateTime columns
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

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


def _import_log_df(folder_path: Path) -> pd.DataFrame:
    file_path = folder_path / "Log.txt"
    if not file_path.is_file():
        raise FileNotFoundError(f"Log file not found: {file_path}")

    dtype = {
        "DateTime": "string",
        "LogCategory": "string",
        "LogType": "string",
        "Cage": "UInt8",
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
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="ISO8601",
        utc=False,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

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
