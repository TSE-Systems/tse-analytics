from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Variable, Aggregation
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class ActimotLoader:
    @staticmethod
    def load(filename: str, dataset: Dataset, csv_import_settings: CsvImportSettings) -> ActimotDetails | None:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return ActimotLoader._load_from_csv(path, dataset, csv_import_settings)
        return None

    @staticmethod
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
                cumulative_col_name,
                variables[col].unit,
                f"{col} (cumulative)",
                "float64",
                Aggregation.MEAN,
                False,
            )
            variables[var.name] = var

    @staticmethod
    def _load_from_csv(path: Path, dataset: Dataset, csv_import_settings: CsvImportSettings):
        with open(path) as f:
            lines = f.readlines()

            header_template = "Rel. [s];BoxNr;"
            # looping through each line in the file
            for idx, line in enumerate(lines):
                if header_template in line:
                    header_line_number = idx
                    columns_line = line
                    break

        datetime_column_header = columns_line.split(csv_import_settings.delimiter)[0]

        usecols = [datetime_column_header, "Rel. [s]", "BoxNr", "X (cm)", "Y (cm)", "X", "Y"]

        dtype = {
            datetime_column_header: str,
            "Rel. [s]": np.float64,
            "BoxNr": np.uint8,
            "X (cm)": np.float64,
            "Y (cm)": np.float64,
            "X": str,
            "Y": str,
        }

        # for i in range(1, 65):
        #     usecols.append(f"X{i}")
        #     dtype[f"X{i}"] = np.uint8
        #
        # for i in range(1, 33):
        #     usecols.append(f"Y{i}")
        #     dtype[f"Y{i}"] = np.uint8

        raw_df = pd.read_csv(
            path,
            delimiter=csv_import_settings.delimiter,
            decimal=csv_import_settings.decimal_separator,
            skiprows=header_line_number,  # Skip header part
            low_memory=True,
            usecols=usecols,
            dtype=dtype,
            na_values=["-"],
        )

        # Rename table columns
        raw_df.rename(columns={datetime_column_header: "DateTime", "BoxNr": "Box"}, inplace=True)

        # Convert DateTime column
        raw_df["DateTime"] = pd.to_datetime(
            raw_df["DateTime"],
            format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else "mixed",
            dayfirst=csv_import_settings.day_first,
        )

        box_to_animal_map = {}
        for animal in dataset.animals.values():
            box_to_animal_map[animal.box] = animal.id

        new_df = raw_df.copy()

        new_df.insert(
            new_df.columns.get_loc("Box") + 1,
            "Animal",
            None,
        )

        new_df["Animal"] = new_df["Box"].astype(int)
        new_df.replace({"Animal": box_to_animal_map}, inplace=True)

        new_df = new_df.sort_values(["Box", "DateTime"])
        new_df.reset_index(drop=True, inplace=True)

        # convert categorical types
        new_df = new_df.astype({
            "Animal": "category",
        })

        # Calo Details sampling interval
        sampling_interval = new_df.iloc[1].at["DateTime"] - new_df.iloc[0].at["DateTime"]

        variables: dict[str, Variable] = {}

        actimot_details = ActimotDetails(
            dataset,
            f"ActiMot [sampling: {str(sampling_interval)}]",
            str(path),
            variables,
            new_df,
            sampling_interval,
        )
        return actimot_details
