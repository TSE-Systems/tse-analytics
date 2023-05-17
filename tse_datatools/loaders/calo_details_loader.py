from pathlib import Path
from typing import Optional

import pandas as pd

from tse_datatools.data.calo_details import CaloDetails
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.variable import Variable

DELIMITER = ";"
DECIMAL = "."


class CaloDetailsLoader:
    @staticmethod
    def load(filename: str, dataset: Dataset) -> Optional[CaloDetails]:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return CaloDetailsLoader.__load_from_csv(path, dataset)
        return None

    @staticmethod
    def __load_from_csv(path: Path, dataset: Dataset):
        columns_line = None
        with open(path, "r") as f:
            lines = f.readlines()

            header_template = "Date;Time;Box;Marker;"
            # looping through each line in the file
            for idx, line in enumerate(lines):
                if header_template in line:
                    header_line_number = idx
                    columns_line = line
                    break

        df = pd.read_csv(
            path,
            delimiter=DELIMITER,
            decimal=DECIMAL,
            skiprows=header_line_number,  # Skip header line
            parse_dates={"DateTime": ["Date", "Time"]},
            infer_datetime_format=True,
            encoding='ISO-8859-1',
            na_values="-",
        )

        # Sanitize column names
        new_column_names = {}
        for column in df.columns.values:
            new_column_names[column] = column.split(" ")[0]
        df.rename(columns=new_column_names, inplace=True)

        # Extract variables
        variables: dict[str, Variable] = {}
        if columns_line is not None:
            columns = columns_line.split(DELIMITER)
            for i, item in enumerate(columns):
                # Skip first 'Date', 'Time', 'Box' and 'Marker' columns
                if i < 4:
                    continue
                elements = item.split(" ")
                var_name = elements[0]
                var_unit = ""
                if len(elements) == 2:
                    var_unit = elements[1]
                variable = Variable(name=var_name, unit=var_unit, description="")
                variables[variable.name] = variable

        # Calo Details sampling interval
        sampling_interval = df.iloc[1].at["DateTime"] - df.iloc[0].at["DateTime"]

        calo_details = CaloDetails(dataset, "Calo Details", str(path), variables, df, sampling_interval)
        return calo_details


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = CaloDetailsLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    # dataset = CaloDetailsLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    print(timeit.default_timer() - tic)
