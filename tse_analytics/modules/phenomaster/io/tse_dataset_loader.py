import json
import timeit
from pathlib import Path

import connectorx as cx
import pandas as pd
from loguru import logger

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Animal, Variable
from tse_analytics.core.utils.data import sanitize_dtypes
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values
from tse_analytics.modules.phenomaster.data.variables_helper import cleanup_variables
from tse_analytics.modules.phenomaster.extensions.actimot.io.data_loader import read_actimot_raw
from tse_analytics.modules.phenomaster.extensions.calo.io.data_loader import read_calo_bin
from tse_analytics.modules.phenomaster.extensions.drinkfeed.io.data_loader import read_drinkfeed_bin, read_drinkfeed_raw
from tse_analytics.modules.phenomaster.extensions.grouphousing.io.data_loader import read_grouphousing
from tse_analytics.modules.phenomaster.io import tse_import_settings


def load_tse_dataset(path: Path, import_settings: tse_import_settings.TseImportSettings) -> Dataset | None:
    """
    Loads and processes a PhenoMaster dataset from the specified path and settings.

    This function reads metadata and animal information corresponding to a
    PhenoMaster dataset, initializes a dataset object, and imports additional
    data tables based on the provided import settings. It processes the main
    dataset table, assigns predefined variable properties, and optionally
    imports raw data from ActoMot, drink-feed bin, and calo bin tables, if they
    are present and specified in the import settings.

    :param path:
        A pathlib.Path object representing the directory containing the dataset
        to be loaded.
    :param import_settings:
        An instance of TseImportSettings that specifies which optional data
        sets (ActoMot raw data, drink-feed bin data, calo bin data) should be
        imported along with the PhenoMaster dataset.
    :return:
        A Dataset object containing the processed data, or None
        if the dataset could not be loaded or processed.
    """
    tic = timeit.default_timer()

    metadata = _read_metadata(path)
    animals = _get_animals(metadata["animals"])

    dataset = Dataset(
        metadata["experiment"]["experiment_no"],
        "PhenoMaster dataset",
        "PhenoMaster",
        metadata=metadata,
        animals=animals,
    )

    main_table_df, main_table_vars, main_table_sample_interval = _read_main_table(path, dataset)
    # Assign predefined variables properties
    main_table_vars = assign_predefined_values(main_table_vars)

    datatable = Datatable(
        dataset,
        "Main",
        "Main table output from PhenoMaster experiment.",
        main_table_vars,
        main_table_df,
        {
            "origin": "Main",
            "sample_interval": main_table_sample_interval,
        },
    )
    dataset.add_datatable(datatable)

    # Import ActoMot raw data if present
    if import_settings.import_actimot_raw:
        if tse_import_settings.ACTIMOT_RAW_TABLE in metadata["tables"]:
            datatable = read_actimot_raw(path, dataset)
            dataset.add_raw_datatable("ActiMot", datatable)

    # Import drinkfeed bin data if present
    if import_settings.import_drinkfeed_bin:
        if tse_import_settings.DRINKFEED_BIN_TABLE in metadata["tables"]:
            datatable = read_drinkfeed_bin(path, dataset)
            dataset.add_raw_datatable("DrinkFeed", datatable)

    if import_settings.import_drinkfeed_raw:
        if tse_import_settings.DRINKFEED_RAW_TABLE in metadata["tables"]:
            datatable = read_drinkfeed_raw(path, dataset)
            dataset.add_raw_datatable("DrinkFeed", datatable)

    # Import calo bin data if present
    if import_settings.import_calo_bin:
        if tse_import_settings.CALO_BIN_TABLE in metadata["tables"]:
            datatable = read_calo_bin(path, dataset)
            dataset.add_raw_datatable("Calo", datatable)

    # Import group housing data if present
    if import_settings.import_grouphousing:
        if tse_import_settings.GROUP_HOUSING_TABLE in metadata["tables"]:
            datatable = read_grouphousing(path, dataset)
            dataset.add_raw_datatable("GroupHousing", datatable)

    # Clean up old variables
    cleanup_variables(dataset)

    # Set factors
    dataset.set_factors(dataset.factors)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _read_metadata(path: Path) -> dict:
    df = cx.read_sql(
        f"sqlite:///{path}",
        "SELECT * FROM metadata",
        return_type="pandas",
    )
    metadata_str = df.iloc[0]["json"]
    metadata = json.loads(metadata_str)

    # Convert animal IDs to strings
    for item in metadata["animals"].values():
        item["id"] = str(item["id"])

    # Add standard data fields
    metadata["source_path"] = str(path)
    metadata["experiment_started"] = metadata["experiment"]["start_datetime"]
    metadata["experiment_stopped"] = metadata["experiment"]["end_datetime"]

    # Convert time intervals from [ms] to Timedeltas
    metadata["experiment"]["runtime"] = str(pd.to_timedelta(metadata["experiment"]["runtime"], unit="ms"))
    metadata["experiment"]["cycle_interval"] = str(pd.to_timedelta(metadata["experiment"]["cycle_interval"], unit="ms"))

    # Convert sample intervals from [ms] to Timedeltas
    for table_meta in metadata["tables"].values():
        if "sample_interval" in table_meta:
            table_meta["sample_interval"] = str(pd.to_timedelta(table_meta["sample_interval"], unit="ms"))

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

        # Add Tag property if exists
        if "tag" in item:
            properties["Tag"] = item["tag"]

        # Add RefBox property if exists
        if "ref_box" in item:
            properties["RefBox"] = int(item["ref_box"])

        animal = Animal(
            id=str(item["id"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal

    # Sort animals by ID
    animals = dict(sorted(animals.items()))

    return animals


def _read_main_table(
    path: Path,
    dataset: Dataset,
) -> tuple[pd.DataFrame, dict[str, Variable], pd.Timedelta]:
    metadata = dataset.metadata["tables"][tse_import_settings.MAIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(item["id"], item["unit"], item["description"], item["type"], Aggregation.MEAN, False)
        variables[variable.name] = variable
        dtypes[variable.name] = item["type"]

    # Drop core (default) variables from the list
    variables.pop("DateTime")
    variables.pop("Animal")
    variables.pop("Box")

    # Read measurements data
    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT * FROM {tse_import_settings.MAIN_TABLE}",
        return_type="pandas",
    )

    # Convert types according to metadata
    dtypes = sanitize_dtypes(dtypes)
    df = df.astype(dtypes, errors="ignore")

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns").dt.as_unit(TIME_RESOLUTION_UNIT)

    # Convert animal id to string first
    df["Animal"] = df["Animal"].astype("string")

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    # Sort dataframe
    df.sort_values(by=["DateTime", "Animal"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta column.
    df.insert(
        loc=1,
        column="Timedelta",
        value=(df["DateTime"] - dataset.experiment_started).dt.as_unit(TIME_RESOLUTION_UNIT),
    )

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    return df, variables, sample_interval
