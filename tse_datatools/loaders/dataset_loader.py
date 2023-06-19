from io import StringIO
from pathlib import Path
from typing import Optional, NamedTuple
from collections import namedtuple

import pandas as pd

from tse_datatools.data.animal import Animal
from tse_datatools.data.box import Box
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.variable import Variable

DELIMITER = ";"
DECIMAL = "."

Section = namedtuple("Section", ["lines", "section_start_index", "section_end_index"])


class DatasetLoader:
    @staticmethod
    def load(filename: str) -> Optional[Dataset]:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return DatasetLoader.__load_from_csv(path)
        return None

    @staticmethod
    def __get_header_section(lines: list[str]):
        section = [
            lines[0],
            lines[1]
        ]
        return Section(section, 0, 1)

    @staticmethod
    def __get_animal_section(lines: list[str], start_index: int):
        trimmed_lines = lines[start_index:]
        section_end_index = None
        for idx, line in enumerate(trimmed_lines):
            if line == "":
                section_end_index = idx + start_index
                break
        section = lines[start_index:section_end_index]
        return Section(section, start_index, section_end_index)

    @staticmethod
    def __get_sample_interval_section(lines: list[str], start_index: int):
        line = lines[start_index]
        if "Sample Interval;" in line:
            return Section([line], start_index, start_index+1)
        else:
            return None

    @staticmethod
    def __get_group_section(lines: list[str], start_index: int):
        trimmed_lines = lines[start_index:]
        section_end_index = None
        for idx, line in enumerate(trimmed_lines):
            if line == "":
                section_end_index = idx + start_index
                break
        section = lines[start_index:section_end_index]
        return Section(section, start_index, section_end_index)

    @staticmethod
    def __get_data_section(lines: list[str], start_index: int):
        section = lines[start_index:]
        return Section(section, start_index, len(lines))

    @staticmethod
    def __load_from_csv(path: Path):
        with open(path, "r") as f:
            lines = f.readlines()

        # lines = [line.strip().rstrip(DELIMITER) for line in lines]
        lines = [line.strip() for line in lines]

        header_section = DatasetLoader.__get_header_section(lines)
        animal_section = DatasetLoader.__get_animal_section(lines, header_section.section_end_index + 1)
        sample_interval_section = DatasetLoader.__get_sample_interval_section(lines, animal_section.section_end_index + 1)
        group_section = DatasetLoader.__get_group_section(lines, sample_interval_section.section_end_index + 1) if sample_interval_section is not None else None
        data_section = DatasetLoader.__get_data_section(lines, group_section.section_end_index + 1 if group_section is not None else animal_section.section_end_index + 1)

        boxes: dict[int, Box] = {}
        animals: dict[int, Animal] = {}
        variables: dict[str, Variable] = {}

        for line in animal_section.lines[1:]:
            elements = line.split(DELIMITER)
            animal = Animal(
                id=int(elements[1]),
                box_id=int(elements[0]),
                weight=float(elements[2]),
                text1=elements[3],
                text2=elements[4],
                text3=elements[5] if len(elements) == 6 else "",
            )
            animals[animal.id] = animal

            box = Box(animal.box_id, animal.id)
            boxes[box.id] = box

        data_header = data_section.lines[0].rstrip(DELIMITER)
        columns = data_header.split(DELIMITER)
        data_unit_header = data_section.lines[1].rstrip(DELIMITER)
        columns_unit = data_unit_header.split(DELIMITER)

        for i, item in enumerate(columns):
            # Skip first 'Date', 'Time', 'Animal No.' and 'Box' columns
            if i < 4:
                continue
            variable = Variable(name=item, unit=columns_unit[i], description="")
            variables[variable.name] = variable

        data = data_section.lines[2:]
        data = [line.rstrip(DELIMITER) for line in data]
        csv = "\n".join(data)

        # noinspection PyTypeChecker
        df = pd.read_csv(
            StringIO(csv),
            delimiter=DELIMITER,
            decimal=DECIMAL,
            na_values=["-"],
            names=columns,
            parse_dates=[["Date", "Time"]],
        )

        # Rename table columns
        df.rename(columns={"Date_Time": "DateTime", "Animal No.": "Animal"}, inplace=True)

        # Apply categorical types
        df = df.astype({
            "Animal": "category",
            "Box": "category",
        })

        timedelta = df["DateTime"][1] - df["DateTime"][0]

        # Sort dataframe
        df.sort_values(by=["DateTime", "Box"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Calculate cumulative values
        if "Drink" in df.columns:
            df["DrinkK"] = df.groupby("Box")["Drink"].transform(pd.Series.cumsum)
            var = Variable(name="DrinkK", unit=variables["Drink"].unit, description="")
            variables[var.name] = var

        if "Feed" in df.columns:
            df["FeedK"] = df.groupby("Box")["Feed"].transform(pd.Series.cumsum)
            var = Variable(name="FeedK", unit=variables["Feed"].unit, description="")
            variables[var.name] = var

        start_date_time = df["DateTime"][0]
        df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
        df.insert(loc=2, column="Bin", value=(df["Timedelta"] / timedelta).round().astype(int))

        # Add Run column
        df.insert(loc=5, column="Run", value=1)

        # convert categorical types
        df = df.astype({
            "Bin": "category",
            "Run": "category",
        })

        # Sort variables by name
        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        name = header_section.lines[0].split(DELIMITER)[0]
        description = header_section.lines[0].split(DELIMITER)[1]
        version = header_section.lines[1].split(DELIMITER)[1]

        meta = {
            "Name": name,
            "Description": description,
            "Version": version,
            "Path": str(path),
            "Boxes": [v.get_dict() for i, (k, v) in enumerate(boxes.items())],
            "Animals": [v.get_dict() for i, (k, v) in enumerate(animals.items())],
            "Variables": [v.get_dict() for i, (k, v) in enumerate(variables.items())],
            "Sampling Interval": str(timedelta),
        }

        dataset = Dataset(name, str(path), meta, boxes, animals, variables, df, timedelta)
        return dataset


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = DatasetLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    # dataset = DatasetLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    dataset = DatasetLoader.load("C:\\Users\\anton\\Downloads\\2023-05-24_Test Sample Flow 0.5_90 s per box.csv")
    print(timeit.default_timer() - tic)
