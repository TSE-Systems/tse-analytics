from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd

from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.variable import Variable


delimiter = ';'
decimal = '.'


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

        lines = [line.strip().rstrip(delimiter) for line in lines]

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
            elements = line.split(delimiter)
            animal = Animal(
                id=int(elements[1]),
                box_id=int(elements[0]),
                weight=float(elements[2]),
                text1=elements[3],
                text2=elements[4],
                text3=elements[5]
            )
            animals[animal.id] = animal

            box = Box(animal.box_id, animal.id)
            boxes[box.id] = box

        data_header = lines[data_section_start]
        columns = data_header.split(delimiter)
        data_unit_header = lines[data_section_start + 1]
        data_section = lines[data_section_start + 2:len(lines)]

        for i, item in enumerate(data_unit_header.split(delimiter)):
            if item == '':
                continue
            variable = Variable(name=columns[i], unit=item)
            variables[variable.name] = variable

        csv = '\n'.join(data_section)
        df = pd.read_csv(StringIO(csv), delimiter=delimiter, decimal=decimal, na_values=['-'], names=columns, parse_dates=[['Date', 'Time']],
                         infer_datetime_format=True)
        df.rename(columns={
            "Date_Time": "DateTime",
            "Animal No.": "AnimalNo"
        }, inplace=True)

        # Sort dataframe
        df.sort_values(by=['DateTime', 'Box'], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Calculate cumulative values
        df['DrinkK'] = df.groupby('Box')['Drink'].transform(pd.Series.cumsum)
        var = Variable(name='DrinkK', unit=variables['Drink'].unit)
        variables[var.name] = var

        df['FeedK'] = df.groupby('Box')['Feed'].transform(pd.Series.cumsum)
        var = Variable(name='FeedK', unit=variables['Feed'].unit)
        variables[var.name] = var

        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        name = header[0].split(delimiter)[0]
        description = header[0].split(delimiter)[1]
        version = header[1].split(delimiter)[1]

        meta = {
            "Name": name,
            "Description": description,
            "Version": version,
            "Path": str(path),
            "Boxes": [v.get_dict() for i, (k, v) in enumerate(boxes.items())],
            "Animals": [v.get_dict() for i, (k, v) in enumerate(animals.items())],
            "Variables": [v.get_dict() for i, (k, v) in enumerate(variables.items())]
        }

        dataset = Dataset(name, str(path), meta, boxes, animals, variables, df)
        return dataset


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = DatasetLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    dataset = DatasetLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    print(timeit.default_timer() - tic)
