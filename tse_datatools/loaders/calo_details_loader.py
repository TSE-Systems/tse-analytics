from pathlib import Path
from typing import Optional

import pandas as pd

from tse_datatools.data.calo_details import CaloDetails

DELIMITER = ";"
DECIMAL = "."


class CaloDetailsLoader:
    @staticmethod
    def load(filename: str) -> Optional[CaloDetails]:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return CaloDetailsLoader.__load_from_csv(path)
        return None

    @staticmethod
    def __load_from_csv(path: Path):
        with open(path, "r") as f:
            lines = f.readlines()

            header_template = "Date;Time;Box;Marker;"
            # looping through each line in the file
            for idx, line in enumerate(lines):
                if header_template in line:
                    header_line_number = idx
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

        df.rename(columns={
            "O2 [%]": "O2",
            "CO2 [%]": "CO2",
            "RER ": "RER",
            "VO2(3) [ml/h]": "VO2(3)",
            "VCO2(3) [ml/h]": "VCO2(3)",
            "H(3) [kcal/h]": "H(3)",
        }, inplace=True)

        calo_details_data = CaloDetails(None, "Calo Details", str(path), None, df, None)
        return calo_details_data


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = CaloDetailsLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    # dataset = CaloDetailsLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    print(timeit.default_timer() - tic)
