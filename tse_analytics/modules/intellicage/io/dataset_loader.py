import tempfile
import timeit
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.data.intellicage_raw_data import IntelliCageRawData
from tse_analytics.modules.intellicage.data.main_table_helper import preprocess_main_table


def import_intellicage_dataset(path: Path) -> IntelliCageDataset | None:
    tic = timeit.default_timer()

    with zipfile.ZipFile(path, mode="r") as zip:
        with tempfile.TemporaryDirectory(prefix="tse-analytics-") as tempdir:
            tmp_path = Path(tempdir)
            zip.extractall(tempdir)

            data_descriptor = _import_data_descriptor(tmp_path / "DataDescriptor.xml")
            metadata = _import_metadata(tmp_path / "Sessions.xml")
            animals = _import_animals(tmp_path / "Animals.txt")

            dataset = IntelliCageDataset(
                name=path.stem,
                path=str(path),
                meta={
                    "data_descriptor": data_descriptor,
                    "experiment": metadata,
                    "animals": {k: v.get_dict() for (k, v) in animals.items()},
                },
                animals=animals,
            )

            folder_path = tmp_path / "IntelliCage"
            visits_df = _import_visits_df(folder_path)
            nosepokes_df = _import_nosepokes_df(folder_path)
            environment_df = _import_environment_df(folder_path)
            hardware_events_df = _import_hardware_events_df(folder_path)
            log_df = _import_log_df(folder_path)

            raw_data = IntelliCageRawData(
                visits_df,
                nosepokes_df,
                environment_df,
                hardware_events_df,
                log_df,
            )

            dataset.intellicage_data = IntelliCageData(
                dataset,
                "IntelliCage",
                raw_data,
            )

    dataset = preprocess_main_table(dataset, pd.to_timedelta(1, unit="minute"))

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _import_data_descriptor(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["DataDescriptor"]


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
        "AnimalName": str,
        "AnimalTag": str,
        "Sex": str,
        "GroupName": str,
        "AnimalNotes": str,
    }

    df = pd.read_csv(
        path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    # Replace np.nan with empty strings
    df.fillna({"AnimalNotes": ""}, inplace=True)

    animals = {}
    for index, row in df.iterrows():
        properties = {
            "Tag": row["AnimalTag"],
            "Sex": row["Sex"],
            "Group": row["GroupName"],
            "Notes": row["AnimalNotes"],
        }
        animal = Animal(
            enabled=True,
            id=str(row["AnimalName"]),
            properties=properties,
        )
        animals[animal.id] = animal

    return animals


def _import_visits_df(folder_path: Path) -> pd.DataFrame | None:
    file_path = folder_path / "Visits.txt"
    if not file_path.is_file():
        return None

    dtype = {
        "VisitID": np.int64,
        "AnimalTag": str,
        "Start": str,
        "End": str,
        "ModuleName": str,
        "Cage": np.int8,
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
    )

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    )

    # Convert numeric Enum values to categories
    df = df.astype({
        "ModuleName": "category",
        "CornerCondition": "category",
        "VisitSolution": "category",
    })

    df["CornerCondition"] = df["CornerCondition"].cat.rename_categories({
        -1: "Incorrect",
        0: "Neutral",
        1: "Correct",
    })

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
    file_path = folder_path / "Nosepokes.txt"
    if not file_path.is_file():
        return None

    with open(file_path) as file:
        first_line = file.readline()
        lick_start_time_column = "LickStartTime" in first_line

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
    }

    if lick_start_time_column:
        dtype["LickStartTime"] = str

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
    )

    df["End"] = pd.to_datetime(
        df["End"],
        format="ISO8601",
        utc=False,
    )

    if lick_start_time_column:
        df["LickStartTime"] = pd.to_datetime(
            df["LickStartTime"],
            format="ISO8601",
            utc=False,
        )

    # Convert numeric Enum values to categories
    df = df.astype({
        "SideCondition": "category",
    })

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
        "Cage": np.int8,
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
        "HardwareType": np.int8,
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
        "LogCategory": str,
        "LogType": str,
        "Cage": "Int64",
        "Corner": "Int64",
        "Side": "Int64",
        "LogNotes": str,
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
