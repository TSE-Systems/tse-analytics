from datetime import timedelta
from pathlib import Path

import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails
from tse_analytics.modules.phenomaster.data.pm_dataset import PMDataset


def import_calo_data(filename: str, dataset: PMDataset, csv_import_settings: CsvImportSettings) -> CaloDetails | None:
    path = Path(filename)
    if path.is_file() and path.suffix.lower() == ".csv":
        return _load_from_csv(path, dataset, csv_import_settings)
    return None


def _load_from_csv(path: Path, dataset: PMDataset, csv_import_settings: CsvImportSettings):
    columns_line = None
    with open(path) as f:
        lines = f.readlines()

        header_template = "Date;Time;"
        # looping through each line in the file
        for idx, line in enumerate(lines):
            if header_template in line:
                header_line_number = idx
                columns_line = line
                break

    df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=header_line_number,  # Skip header part
        parse_dates={"DateTime": ["Date", "Time"]},
        encoding="ISO-8859-1",
        na_values="-",
        dayfirst=csv_import_settings.day_first,
    )

    # Convert DateTime column
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="mixed",
        dayfirst=csv_import_settings.day_first,
    )

    # Sanitize column names
    new_column_names = {}
    for column in df.columns.values:
        new_column_names[column] = column.split(" ")[0]
    df.rename(columns=new_column_names, inplace=True)

    # Extract variables
    variables: dict[str, Variable] = {}
    if columns_line is not None:
        columns = columns_line.split(csv_import_settings.delimiter)
        for i, item in enumerate(columns):
            # Skip first 'Date', 'Time', 'Box' and 'Marker' columns
            if i < 4:
                continue
            elements = item.split(" ")
            var_name = elements[0]
            var_unit = ""
            if len(elements) == 2:
                var_unit = elements[1]
            variable = Variable(var_name, var_unit, "", "float64", Aggregation.MEAN, False)
            variables[variable.name] = variable

    # Calo Details sampling interval
    sampling_interval = df.iloc[1].at["DateTime"] - df.iloc[0].at["DateTime"]

    df = df.sort_values(["Box", "DateTime"])

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

    calo_details = CaloDetails(
        dataset,
        f"Calo [sampling: {str(sampling_interval)}]",
        str(path),
        variables,
        df,
        sampling_interval,
    )
    return calo_details
