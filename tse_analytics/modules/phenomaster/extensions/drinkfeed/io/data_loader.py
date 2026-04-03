from pathlib import Path

import connectorx as cx
import pandas as pd
import pyarrow as pa

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.core.utils.data import sanitize_dtypes
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.extensions.drinkfeed.data.drinkfeed_bin_data import DrinkFeedBinData
from tse_analytics.modules.phenomaster.extensions.drinkfeed.data.drinkfeed_raw_data import DrinkFeedRawData
from tse_analytics.modules.phenomaster.io import tse_import_settings


def read_drinkfeed_bin(path: Path, dataset: PhenoMasterDataset) -> DrinkFeedBinData:
    metadata = dataset.metadata["tables"][tse_import_settings.DRINKFEED_BIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variable list
    skipped_variables = ["DateTime", "Box", "Animal"]
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

    # Read measurement data
    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT * FROM {tse_import_settings.DRINKFEED_BIN_TABLE}",
        return_type="pandas",
    )

    # Convert types according to metadata
    dtypes = sanitize_dtypes(dtypes)
    df = df.astype(dtypes, errors="ignore")

    # Convert DateTime from POSIX format
    df["DateTime"] = (
        pd
        .to_datetime(df["DateTime"], origin="unix", unit="ns")
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Add Animal column
    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[str(animal.properties["Box"])] = animal.id

    if "Animal" not in df.columns:
        df.insert(
            df.columns.get_loc("Box"),
            "Animal",
            df["Box"].astype("string[pyarrow]").replace(box_to_animal_map),
        )
    else:
        df["Animal"] = df["Animal"].astype("string[pyarrow]")

    df = df.astype({
        "Animal": "category",
    })

    # Sort by DateTime column
    df.sort_values(by=["DateTime", "Animal"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    raw_datatable = Datatable(
        dataset,
        tse_import_settings.DRINKFEED_BIN_TABLE,
        f"Raw {tse_import_settings.DRINKFEED_BIN_TABLE} datatable",
        variables,
        df,
        {
            "origin_path": str(path),
            "sampling_interval": sample_interval,
        },
    )

    data = DrinkFeedBinData(
        dataset,
        tse_import_settings.DRINKFEED_BIN_TABLE,
        raw_datatable,
    )

    return data


def read_drinkfeed_raw(path: Path, dataset: PhenoMasterDataset) -> DrinkFeedRawData:
    table_metadata = dataset.metadata["tables"][tse_import_settings.DRINKFEED_RAW_TABLE]
    hardware_metadata = dataset.metadata["hardware"][tse_import_settings.DRINKFEED_RAW_TABLE]

    # Prepare dtypes
    dtypes = {}
    for item in table_metadata["columns"].values():
        dtypes[item["id"]] = item["type"]

    # Read measurements data
    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT * FROM {tse_import_settings.DRINKFEED_RAW_TABLE}",
        return_type="pandas",
    )

    # Convert types according to metadata
    dtypes = sanitize_dtypes(dtypes)
    df = df.astype(dtypes, errors="ignore")

    # Convert DateTime from POSIX format
    df["DateTime"] = (
        pd
        .to_datetime(df["DateTime"], origin="unix", unit="ns")
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    # Sort by DateTime column
    df.sort_values(by=["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert dict keys type from str to int
    param_to_sensor_mapping = {int(k): v for k, v in hardware_metadata["params"].items()}
    # Replace Param column
    df.insert(
        df.columns.get_loc("Box") + 1,
        "Sensor",
        df["Param"].replace(param_to_sensor_mapping),
    )
    df.drop(columns=["Param"], inplace=True)

    # Add Animal column
    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    df.insert(
        df.columns.get_loc("Box") + 1,
        "Animal",
        df["Box"].replace(box_to_animal_map),
    )

    df = df.astype({
        "Animal": "category",
        "Sensor": "category",
    })

    variables: dict[str, Variable] = {}
    sensors = df["Sensor"].unique().tolist()
    for sensor in sensors:
        variables[sensor] = Variable(
            sensor,
            "",
            "Sensor value",
            "float64[pyarrow]",
            Aggregation.MEAN,
            False,
        )

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    raw_datatable = Datatable(
        dataset,
        tse_import_settings.DRINKFEED_RAW_TABLE,
        f"Raw {tse_import_settings.DRINKFEED_RAW_TABLE} datatable",
        variables,
        df,
        {
            "origin_path": str(path),
        },
    )

    data = DrinkFeedRawData(
        dataset,
        tse_import_settings.DRINKFEED_RAW_TABLE,
        raw_datatable,
    )

    return data


def import_drinkfeed_bin_csv_data(
    filename: str,
    dataset: PhenoMasterDataset,
    csv_import_settings: CsvImportSettings,
) -> DrinkFeedBinData | None:
    path = Path(filename)
    if not path.is_file() or path.suffix.lower() != ".csv":
        return None

    with open(path) as f:
        lines = f.readlines()

        header_template = "Date;Time;"
        # looping through each line in the file
        for idx, line in enumerate(lines):
            if header_template in line:
                header_line_number = idx
                columns_line = line
                break

    raw_df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=header_line_number,  # Skip header part
        encoding="ISO-8859-1",
    )

    raw_df.insert(
        0,
        "DateTime",
        pd
        .to_datetime(
            raw_df["Date"] + " " + raw_df["Time"],
            format="mixed",
            dayfirst=csv_import_settings.day_first,
        )
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT))),
    )
    raw_df.drop(columns=["Date", "Time"], inplace=True)

    # Calculate sampling interval
    sampling_interval = raw_df.iloc[1].at["DateTime"] - raw_df.iloc[0].at["DateTime"]

    # Find box numbers
    box_numbers = []
    for column in raw_df.columns.values:
        if "Box" in column:
            box_numbers.append(int(column.split(":")[0].replace("Box", "")))
    box_numbers = list(set(box_numbers))

    # Check available variables
    drink1_present = "Drink1" in columns_line
    drink2_present = "Drink2" in columns_line
    feed1_present = "Feed1" in columns_line
    feed2_present = "Feed2" in columns_line
    weight_present = "Weight" in columns_line
    drink_present = "Drink" in columns_line and (not drink1_present and not drink2_present)
    feed_present = "Feed" in columns_line and (not feed1_present and not feed2_present)

    # Build new dataframe
    variables: dict[str, Variable] = {}
    if drink1_present:
        variables["Drink1"] = Variable("Drink1", "[ml]", "Drink1 sensor", "float64", Aggregation.MEAN, False)
    if feed1_present:
        variables["Feed1"] = Variable("Feed1", "[g]", "Feed1 sensor", "float64", Aggregation.MEAN, False)
    if drink2_present:
        variables["Drink2"] = Variable("Drink2", "[ml]", "Drink2 sensor", "float64", Aggregation.MEAN, False)
    if feed2_present:
        variables["Feed2"] = Variable("Feed2", "[g]", "Feed2 sensor", "float64", Aggregation.MEAN, False)
    if weight_present:
        variables["Weight"] = Variable("Weight", "[g]", "Animal weight", "float64", Aggregation.MEAN, False)
    if drink_present:
        variables["Drink"] = Variable("Drink", "[ml]", "Drink sensor", "float64", Aggregation.MEAN, False)
    if feed_present:
        variables["Feed"] = Variable("Feed", "[g]", "Feed sensor", "float64", Aggregation.MEAN, False)

    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    new_df = None
    for box_number in box_numbers:
        box_df = pd.DataFrame.from_dict({
            "DateTime": raw_df["DateTime"],
            "Animal": box_to_animal_map[box_number],
            "Box": box_number,
        })
        if drink1_present:
            box_df["Drink1"] = raw_df[f"Box{box_number}: Drink1"]
        if feed1_present:
            box_df["Feed1"] = raw_df[f"Box{box_number}: Feed1"]
        if drink2_present:
            box_df["Drink2"] = raw_df[f"Box{box_number}: Drink2"]
        if feed2_present:
            box_df["Feed2"] = raw_df[f"Box{box_number}: Feed2"]
        if weight_present:
            box_df["Weight"] = raw_df[f"Box{box_number}: Weight"]
        if drink_present:
            box_df["Drink"] = raw_df[f"Box{box_number}: Drink"]
        if feed_present:
            box_df["Feed"] = raw_df[f"Box{box_number}: Feed"]

        if new_df is None:
            new_df = box_df
        else:
            new_df = pd.concat([new_df, box_df], ignore_index=True)

    new_df = new_df.sort_values(["Box", "DateTime"])
    new_df.reset_index(drop=True, inplace=True)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": "category",
        "Box": "uint16[pyarrow]",
    })

    # Convert to pyarrow backend
    new_df = new_df.convert_dtypes(dtype_backend="pyarrow")

    raw_datatable = Datatable(
        dataset,
        tse_import_settings.DRINKFEED_BIN_TABLE,
        f"Raw {tse_import_settings.DRINKFEED_BIN_TABLE} datatable",
        variables,
        new_df,
        {
            "origin_path": str(path),
            "sampling_interval": sampling_interval,
        },
    )

    data = DrinkFeedBinData(
        dataset,
        tse_import_settings.DRINKFEED_BIN_TABLE,
        raw_datatable,
    )
    return data
