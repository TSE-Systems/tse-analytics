import json
import sqlite3
import timeit
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Animal, Factor, Variable
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values
from tse_analytics.modules.phenomaster.io.tse_import_settings import TseImportSettings
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData

CHUNK_SIZE = 1000000

ACTIMOT_RAW_TABLE = "actimot_raw"
DRINKFEED_BIN_TABLE = "drinkfeed_bin"
CALO_BIN_TABLE = "calo_bin"


def load_tse_dataset(path: Path, import_settings: TseImportSettings) -> PhenoMasterDataset | None:
    tic = timeit.default_timer()

    metadata = _read_metadata(path)
    animals = _get_animals(metadata["animals"])

    dataset = PhenoMasterDataset(
        name=metadata["experiment"]["experiment_no"],
        description="PhenoMaster dataset",
        path=str(path),
        metadata=metadata,
        animals=animals,
    )

    main_table_df, main_table_vars, main_table_sampling_interval = _read_main_table(path, dataset)
    # Assign predefined variables properties
    main_table_vars = assign_predefined_values(main_table_vars)

    datatable = Datatable(
        dataset,
        "Main",
        "Main table output from PhenoMaster experiment.",
        main_table_vars,
        main_table_df,
        main_table_sampling_interval,
    )
    dataset.add_datatable(datatable)

    # Import ActoMot raw data if present
    if import_settings.import_actimot_raw:
        if ACTIMOT_RAW_TABLE in metadata["tables"]:
            actimot_data = _read_actimot_raw(path, dataset)
            dataset.actimot_data = actimot_data

    # Import drinkfeed bin data if present
    if import_settings.import_drinkfeed_bin:
        if DRINKFEED_BIN_TABLE in metadata["tables"]:
            drinkfeed_data = _read_drinkfeed_bin(path, dataset)
            dataset.drinkfeed_data = drinkfeed_data

    # Import calo bin data if present
    if import_settings.import_calo_bin:
        if CALO_BIN_TABLE in metadata["tables"]:
            calo_data = _read_calo_bin(path, dataset)
            dataset.calo_data = calo_data

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _read_metadata(path: Path) -> dict:
    with sqlite3.connect(path, check_same_thread=False) as connection:
        df = pd.read_sql_query(
            "SELECT * FROM metadata",
            connection,
        )
        metadata_str = df.iloc[0]["json"]
    metadata = json.loads(metadata_str)

    # Convert animal IDs to strings
    for item in metadata["animals"].values():
        item["id"] = str(item["id"])

    # Convert time intervals from [ms] to Timedeltas
    metadata["experiment"]["runtime"] = str(pd.to_timedelta(metadata["experiment"]["runtime"], unit="ms"))
    metadata["experiment"]["cycle_interval"] = str(pd.to_timedelta(metadata["experiment"]["cycle_interval"], unit="ms"))

    if "main_table" in metadata["tables"]:
        metadata["tables"]["main_table"]["sample_interval"] = str(
            pd.to_timedelta(metadata["tables"]["main_table"]["sample_interval"], unit="ms")
        )

    if "actimot_raw" in metadata["tables"]:
        metadata["tables"]["actimot_raw"]["sample_interval"] = str(
            pd.to_timedelta(metadata["tables"]["actimot_raw"]["sample_interval"], unit="ms")
        )

    return metadata


def _get_animals(data: dict) -> dict[str, Animal]:
    animals: dict[str, Animal] = {}
    for index, item in enumerate(data.values()):
        properties = {
            "Box": int(item["box"]),
            "Weight": float(item["weight"]),
            "Text1": item["text1"],
            "Text2": item["text2"],
            "Text3": item["text3"],
        }
        animal = Animal(
            enabled=bool(item["enabled"]),
            id=str(item["id"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
    return animals


def _get_factors(data: dict) -> dict[str, Factor]:
    factors: dict[str, Factor] = {}
    for item in data.values():
        factor = Factor(name=item["id"])
        factors[factor.name] = factor
    return factors


def _read_main_table(
    path: Path,
    dataset: PhenoMasterDataset,
) -> tuple[pd.DataFrame, dict[str, Variable], pd.Timedelta]:
    metadata = dataset.metadata["tables"]["main_table"]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(item["id"], item["unit"], item["description"], item["type"], Aggregation.MEAN, False)
        variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Drop core (default) variables from the list
    variables.pop("DateTime")
    variables.pop("Animal")
    variables.pop("Box")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            "SELECT * FROM main_table",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Convert animal id to string first
    df["Animal"] = df["Animal"].astype(str)

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    # Sort dataframe
    df.sort_values(by=["DateTime", "Box"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta and Bin columns
    start_date_time = dataset.experiment_started
    df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
    df.insert(loc=2, column="Bin", value=(df["Timedelta"] / sample_interval).round().astype(int))

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    return df, variables, sample_interval


def _read_actimot_raw(path: Path, dataset: PhenoMasterDataset) -> ActimotData:
    metadata = dataset.metadata["tables"][ACTIMOT_RAW_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box", "X1", "X2", "Y1", "Y2", "Z1", "Z2"]
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            item["id"],
            item["unit"],
            item["description"],
            item["type"],
            Aggregation.MEAN,
            False,
        )
        if variable.name not in skipped_variables:
            variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            f"SELECT * FROM {ACTIMOT_RAW_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            chunk["X"] = np.left_shift(chunk["X2"].to_numpy(dtype=np.uint64), 32) + chunk["X1"].to_numpy(
                dtype=np.uint64
            )
            chunk.rename(columns={"Y1": "Y"}, inplace=True)
            chunk.drop(columns=["X1", "X2"], inplace=True)
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    actimot_data = ActimotData(
        dataset,
        ACTIMOT_RAW_TABLE,
        str(path),
        variables,
        df,
        sample_interval,
    )

    return actimot_data


def _read_drinkfeed_bin(path: Path, dataset: PhenoMasterDataset) -> DrinkFeedData:
    metadata = dataset.metadata["tables"][DRINKFEED_BIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box"]
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            item["id"],
            item["unit"],
            item["description"],
            item["type"],
            Aggregation.MEAN,
            False,
        )
        if variable.name not in skipped_variables:
            variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            f"SELECT * FROM {DRINKFEED_BIN_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Add Animal column
    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id
    df["Animal"] = df["Box"].replace(box_to_animal_map)
    df = df.astype({
        "Animal": "category",
    })

    drinkfeed_data = DrinkFeedData(
        dataset,
        DRINKFEED_BIN_TABLE,
        str(path),
        variables,
        df,
        sample_interval,
    )

    return drinkfeed_data


def _read_calo_bin(path: Path, dataset: PhenoMasterDataset) -> CaloData:
    metadata = dataset.metadata["tables"][CALO_BIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box"]
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            item["id"],
            item["unit"],
            item["description"],
            item["type"],
            Aggregation.MEAN,
            False,
        )
        if variable.name not in skipped_variables:
            variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            f"SELECT * FROM {CALO_BIN_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Sort dataframe
    df.sort_values(["Box", "DateTime"], inplace=True)

    # Assign bins
    previous_timestamp = None
    previous_box = None
    bins = []
    offsets = []
    timedeltas = []
    time_gap = timedelta(seconds=10)
    offset = 0
    for row in df.itertuples():
        timestamp = row.DateTime
        box = row.Box

        if box != previous_box:
            start_timestamp = timestamp

        if previous_timestamp is None:
            bins = [0]
        elif timestamp - previous_timestamp > time_gap:
            bin_number = bins[-1]
            bin_number = bin_number + 1

            offset = 0

            # reset bin number for a new box
            if box != previous_box:
                bin_number = 0

            bins.append(bin_number)
            start_timestamp = timestamp
        else:
            bin_number = bins[-1]

            # reset bin number for a new box
            if box != previous_box:
                bin_number = 0
                offset = 0

            bins.append(bin_number)

        if box != previous_box:
            previous_box = box

        td = timestamp - start_timestamp
        timedeltas.append(td)

        # offset = td.total_seconds()
        offsets.append(offset)
        offset = offset + 1
        previous_timestamp = timestamp

    df.insert(1, "Timedelta", timedeltas)
    df.insert(2, "Bin", bins)
    df.insert(3, "Offset", offsets)

    calo_data = CaloData(
        dataset,
        CALO_BIN_TABLE,
        str(path),
        variables,
        df,
        sample_interval,
    )

    return calo_data
