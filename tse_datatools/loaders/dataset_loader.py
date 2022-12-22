from io import StringIO
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.variable import Variable


DELIMITER = ';'
DECIMAL = '.'


class DatasetLoader:

    @staticmethod
    def load(filename: str) -> Optional[Dataset]:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return DatasetLoader.__load_from_csv(path)
        return None

    @staticmethod
    def __load_from_csv(path: Path):
        with open(path, "r") as f:
            lines = f.readlines()

        lines = [line.strip().rstrip(DELIMITER) for line in lines]

        header = [lines[0], lines[1]]

        data_section_start = None
        for num, line in enumerate(lines, 2):
            if line == "":
                data_section_start = num - 1
                break

        animal_section = lines[3:data_section_start - 1]

        boxes: dict[int, Box] = {}
        animals: dict[int, Animal] = {}
        variables: dict[str, Variable] = {}

        for line in animal_section:
            elements = line.split(DELIMITER)
            animal = Animal(
                id=int(elements[1]),
                box_id=int(elements[0]),
                weight=float(elements[2]),
                text1=elements[3],
                text2=elements[4],
                text3=elements[5] if len(elements) == 6 else ""
            )
            animals[animal.id] = animal

            box = Box(animal.box_id, animal.id)
            boxes[box.id] = box

        data_header = lines[data_section_start]
        columns = data_header.split(DELIMITER)
        data_unit_header = lines[data_section_start + 1]
        data_section = lines[data_section_start + 2:len(lines)]
        columns_unit = data_unit_header.split(DELIMITER)

        for i, item in enumerate(columns):
            # Skip first 'Date', 'Time', 'Animal No.' and 'Box' columns
            if i < 4:
                continue
            variable = Variable(name=item, unit=columns_unit[i], description='')
            variables[variable.name] = variable

        csv = '\n'.join(data_section)

        # noinspection PyTypeChecker
        df = pd.read_csv(
            StringIO(csv),
            delimiter=DELIMITER,
            decimal=DECIMAL,
            na_values=['-'],
            names=columns,
            parse_dates=[['Date', 'Time']],
            infer_datetime_format=True
        )

        # Rename table columns
        df.rename(columns={
            "Date_Time": "DateTime",
            "Animal No.": "Animal"
        }, inplace=True)

        # Apply categorical types
        df['Animal'] = df['Animal'].astype('category')
        df['Box'] = df['Box'].astype('category')

        timedelta = df['DateTime'][1] - df['DateTime'][0]

        # Sort dataframe
        df.sort_values(by=['DateTime', 'Box'], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Calculate cumulative values
        if 'Drink' in df.columns:
            df['DrinkK'] = df.groupby('Box')['Drink'].transform(pd.Series.cumsum)
            var = Variable(name='DrinkK', unit=variables['Drink'].unit, description='')
            variables[var.name] = var

        if 'Feed' in df.columns:
            df['FeedK'] = df.groupby('Box')['Feed'].transform(pd.Series.cumsum)
            var = Variable(name='FeedK', unit=variables['Feed'].unit, description='')
            variables[var.name] = var

        start_date_time = df['DateTime'][0]
        df.insert(loc=1, column='Timedelta', value=df['DateTime'] - start_date_time)
        df.insert(loc=2, column='Bin', value=(df["Timedelta"] / timedelta).round().astype(int))
        df['Bin'] = df['Bin'].astype('category')

        df.insert(loc=5, column='Group', value=np.NaN)
        df["Group"] = df["Group"].astype('category')

        # Add Run column
        df.insert(loc=6, column='Run', value=1)
        df['Run'] = df['Run'].astype('category')

        # Sort variables by name
        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        name = header[0].split(DELIMITER)[0]
        description = header[0].split(DELIMITER)[1]
        version = header[1].split(DELIMITER)[1]

        meta = {
            "Name": name,
            "Description": description,
            "Version": version,
            "Path": str(path),
            "Boxes": [v.get_dict() for i, (k, v) in enumerate(boxes.items())],
            "Animals": [v.get_dict() for i, (k, v) in enumerate(animals.items())],
            "Variables": [v.get_dict() for i, (k, v) in enumerate(variables.items())],
            "Sampling Interval": str(timedelta)
        }

        dataset = Dataset(name, str(path), meta, boxes, animals, variables, df, timedelta)
        return dataset


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = DatasetLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    dataset = DatasetLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    print(timeit.default_timer() - tic)
