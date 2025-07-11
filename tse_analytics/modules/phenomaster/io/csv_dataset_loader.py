"""
PhenoMaster CSV Dataset Loader Module

This module provides functionality for loading PhenoMaster datasets from CSV files.
It parses the specific format of CSV files exported by PhenoMaster systems, which
typically contain several sections:
- Header section: Contains metadata about the experiment
- Animal section: Contains information about the animals in the experiment
- Sample interval section: Contains information about the sampling intervals
- Group section: Contains information about animal grouping
- Data section: Contains the actual measurement data

The module extracts information from these sections to create a structured
PhenoMasterDataset object that can be used for analysis and visualization.
"""

from collections import namedtuple
from io import StringIO
from pathlib import Path

import pandas as pd

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Animal, Variable
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset

Section = namedtuple("Section", ["lines", "section_start_index", "section_end_index"])


def load_csv_dataset(path: Path, csv_import_settings: CsvImportSettings) -> PhenoMasterDataset | None:
    """
    Load a PhenoMaster dataset from a CSV file.

    This function parses a CSV file exported by a PhenoMaster system and creates
    a PhenoMasterDataset object containing the data. It extracts information from
    various sections of the file (header, animal, sample interval, group, data)
    and organizes it into a structured dataset.

    Args:
        path (Path): Path to the CSV file to load
        csv_import_settings (CsvImportSettings): Settings for CSV import, including
                                                delimiter, decimal separator, etc.

    Returns:
        PhenoMasterDataset | None: A dataset containing the loaded data, or None if loading failed
    """
    with open(path) as f:
        lines = f.readlines()

    # lines = [line.strip().rstrip(DELIMITER) for line in lines]
    lines = [line.strip() for line in lines]

    header_section = _get_header_section(lines)
    animal_section = _get_animal_section(lines, header_section.section_end_index + 1)
    sample_interval_section = _get_sample_interval_section(lines, animal_section.section_end_index + 1)
    group_section = (
        _get_group_section(lines, sample_interval_section.section_end_index + 1)
        if sample_interval_section is not None
        else None
    )
    data_section = _get_data_section(
        lines,
        group_section.section_end_index + 1 if group_section is not None else animal_section.section_end_index + 1,
    )

    animals: dict[str, Animal] = {}
    variables: dict[str, Variable] = {}

    for index, line in enumerate(animal_section.lines[1:]):
        elements = line.split(csv_import_settings.delimiter)
        properties = {
            "Box": int(elements[0]),
            "Weight": float(elements[2].replace(",", ".")),
            "Text1": elements[3],
            "Text2": elements[4],
            "Text3": elements[5] if len(elements) == 6 else "",
        }
        animal = Animal(
            enabled=True,
            id=elements[1],
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal

    data_header = data_section.lines[0].rstrip(csv_import_settings.delimiter)
    columns = data_header.split(csv_import_settings.delimiter)

    data_unit_header = data_section.lines[1].rstrip(csv_import_settings.delimiter)
    columns_unit = data_unit_header.split(csv_import_settings.delimiter)

    # Check if Date and Time columns are separate
    datetime_separate = columns[0] == "Date"

    for i, item in enumerate(columns):
        if datetime_separate:
            # Skip first 'Date', 'Time', 'Animal No.' and 'Box' columns
            if i < 4:
                continue
        else:
            # Skip first 'Date Time', 'Animal No.' and 'Box' columns
            if i < 3:
                continue
        variable = Variable(item, columns_unit[i], "", "float64", Aggregation.MEAN, False)
        variables[variable.name] = variable

    data = data_section.lines[2:]
    data = [line.rstrip(csv_import_settings.delimiter) for line in data]
    csv = "\n".join(data)

    parse_dates = [["Date", "Time"]] if datetime_separate else False

    # noinspection PyTypeChecker
    df = pd.read_csv(
        StringIO(csv),
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        na_values=["-"],
        names=columns,
        parse_dates=parse_dates,
        dayfirst=csv_import_settings.day_first,
    )

    # TODO: Drop "Box" column?
    # df.drop(columns=["Box"], inplace=True)

    # Rename table columns
    df.rename(columns={"Date_Time": "DateTime", "Date Time": "DateTime", "Animal No.": "Animal"}, inplace=True)

    # Convert DateTime column
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format="mixed",
        dayfirst=csv_import_settings.day_first,
    )

    # Apply categorical types
    df = df.astype({
        "Animal": "str",
    })

    df = df.astype({
        "Animal": "category",
    })

    # find sampling interval
    timedeltas = []
    for index in range(1, 6):
        timedeltas.append(df["DateTime"][index] - df["DateTime"][index - 1])
    timedelta = _most_frequent(timedeltas)

    # Sort dataframe
    df.sort_values(by=["DateTime", "Animal"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    start_date_time = df.at[0, "DateTime"]
    end_date_time = df["DateTime"].iat[-1]
    df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
    df.insert(loc=2, column="Bin", value=(df["Timedelta"] / timedelta).round().astype(int))

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    # Assign predefined variables properties
    variables = assign_predefined_values(variables)

    name = header_section.lines[0].split(csv_import_settings.delimiter)[0]
    description = header_section.lines[0].split(csv_import_settings.delimiter)[1]
    version_section = header_section.lines[1].split(csv_import_settings.delimiter)
    if len(version_section) > 1:
        version = version_section[1]
    else:
        version = version_section[0]

    buf = StringIO()
    df.info(buf=buf)

    metadata = {
        "name": name,
        "description": description,
        "source_path": str(path),
        "experiment_started": str(start_date_time),
        "experiment_stopped": str(end_date_time),
        "experiment": {
            "pm_version": version,
        },
        "animals": {k: v.get_dict() for (k, v) in animals.items()},
        "tables": {
            "main_table": {
                "id": "main_table",
                "sample_interval": str(timedelta),
                "columns": {k: v.get_dict() for (k, v) in variables.items()},
            }
        },
    }

    dataset = PhenoMasterDataset(
        metadata=metadata,
        animals=animals,
    )

    datatable = Datatable(
        dataset,
        "Main",
        "Main table output from PhenoMaster experiment.",
        variables,
        df,
        timedelta,
    )
    dataset.add_datatable(datatable)

    return dataset


def _get_header_section(lines: list[str]) -> Section:
    """
    Extract the header section from the CSV file.

    The header section typically contains the experiment name, description,
    and version information in the first two lines of the file.

    Args:
        lines (list[str]): All lines from the CSV file

    Returns:
        Section: A named tuple containing the header lines and their indices
    """
    section = [lines[0], lines[1]]
    return Section(section, 0, 1)


def _get_animal_section(lines: list[str], start_index: int):
    trimmed_lines = lines[start_index:]
    section_end_index = None
    for idx, line in enumerate(trimmed_lines):
        if line == "":
            section_end_index = idx + start_index
            break
    section = lines[start_index:section_end_index]
    return Section(section, start_index, section_end_index)


def _get_sample_interval_section(lines: list[str], start_index: int):
    line = lines[start_index]
    if "Sample Interval;" in line:
        return Section([line], start_index, start_index + 1)
    else:
        return None


def _get_group_section(lines: list[str], start_index: int):
    trimmed_lines = lines[start_index:]
    section_end_index = None
    for idx, line in enumerate(trimmed_lines):
        if line == "":
            section_end_index = idx + start_index
            break
    section = lines[start_index:section_end_index]
    return Section(section, start_index, section_end_index)


def _get_data_section(lines: list[str], start_index: int):
    section = lines[start_index:]
    return Section(section, start_index, len(lines))


def _most_frequent(lst: list):
    return max(set(lst), key=lst.count)
