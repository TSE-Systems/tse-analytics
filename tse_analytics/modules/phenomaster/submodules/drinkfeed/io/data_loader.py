from pathlib import Path

import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData


def import_drinkfeed_data(
    filename: str, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings
) -> DrinkFeedData | None:
    path = Path(filename)
    if path.is_file() and path.suffix.lower() == ".csv":
        return _load_from_csv(path, dataset, csv_import_settings)
    return None


def _add_cumulative_columns(df: pd.DataFrame, origin_name: str, variables: dict[str, Variable]):
    cols = [col for col in df.columns if origin_name in col]
    for col in cols:
        cumulative_col_name = col + "C"
        df.insert(
            df.columns.get_loc(col) + 1,
            cumulative_col_name,
            df.groupby("Box", observed=False)[col].transform(pd.Series.cumsum),
        )
        var = Variable(
            cumulative_col_name, variables[col].unit, f"{col} (cumulative)", "float64", Aggregation.MEAN, False
        )
        variables[var.name] = var


def _load_from_csv(path: Path, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings):
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
        parse_dates={"DateTime": ["Date", "Time"]},
        encoding="ISO-8859-1",
        dayfirst=csv_import_settings.day_first,
    )

    # Convert DateTime column
    raw_df["DateTime"] = pd.to_datetime(
        raw_df["DateTime"],
        format="mixed",
        dayfirst=csv_import_settings.day_first,
    )

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
    new_columns = ["DateTime", "Animal", "Box"]
    variables: dict[str, Variable] = {}
    if drink1_present:
        new_columns.append("Drink1")
        variables["Drink1"] = Variable("Drink1", "[ml]", "Drink1 sensor", "float64", Aggregation.MEAN, False)
    if feed1_present:
        new_columns.append("Feed1")
        variables["Feed1"] = Variable("Feed1", "[g]", "Feed1 sensor", "float64", Aggregation.MEAN, False)
    if drink2_present:
        new_columns.append("Drink2")
        variables["Drink2"] = Variable("Drink2", "[ml]", "Drink2 sensor", "float64", Aggregation.MEAN, False)
    if feed2_present:
        new_columns.append("Feed2")
        variables["Feed2"] = Variable("Feed2", "[g]", "Feed2 sensor", "float64", Aggregation.MEAN, False)
    if weight_present:
        new_columns.append("Weight")
        variables["Weight"] = Variable("Weight", "[g]", "Animal weight", "float64", Aggregation.MEAN, False)
    if drink_present:
        new_columns.append("Drink")
        variables["Drink"] = Variable("Drink", "[ml]", "Drink sensor", "float64", Aggregation.MEAN, False)
    if feed_present:
        new_columns.append("Feed")
        variables["Feed"] = Variable("Feed", "[g]", "Feed sensor", "float64", Aggregation.MEAN, False)

    new_df = pd.DataFrame(columns=new_columns)

    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

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

        new_df = pd.concat([new_df, box_df], ignore_index=True)

    new_df = new_df.sort_values(["Box", "DateTime"])
    new_df.reset_index(drop=True, inplace=True)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": "category",
    })

    # Calculate cumulative values
    if drink1_present:
        _add_cumulative_columns(new_df, "Drink1", variables)
    if feed1_present:
        _add_cumulative_columns(new_df, "Feed1", variables)
    if drink2_present:
        _add_cumulative_columns(new_df, "Drink2", variables)
    if feed2_present:
        _add_cumulative_columns(new_df, "Feed2", variables)
    if drink_present:
        _add_cumulative_columns(new_df, "Drink", variables)
    if feed_present:
        _add_cumulative_columns(new_df, "Feed", variables)

    drinkfeed_data = DrinkFeedData(
        dataset,
        f"DrinkFeed Data",
        str(path),
        variables,
        new_df,
    )
    return drinkfeed_data
