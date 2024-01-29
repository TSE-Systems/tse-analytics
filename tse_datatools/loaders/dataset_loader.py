from collections import namedtuple
from io import StringIO
from pathlib import Path

import pandas as pd

from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.variable import Variable

DELIMITER = ";"
DECIMAL = "."

Section = namedtuple("Section", ["lines", "section_start_index", "section_end_index"])


def most_frequent(lst: list):
    return max(set(lst), key=lst.count)


class DatasetLoader:
    @staticmethod
    def load(filename: str) -> Dataset | None:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return DatasetLoader.__load_from_csv(path)
        return None

    @staticmethod
    def __get_header_section(lines: list[str]):
        section = [lines[0], lines[1]]
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
            return Section([line], start_index, start_index + 1)
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
    def __add_cumulative_columns(df: pd.DataFrame, origin_name: str, variables: dict[str, Variable]):
        cols = [col for col in df.columns if origin_name in col]
        for col in cols:
            cumulative_col_name = col + "C"
            df[cumulative_col_name] = df.groupby("Box", observed=False)[col].transform(pd.Series.cumsum)
            var = Variable(name=cumulative_col_name, unit=variables[col].unit, description=f"{col} (cumulative)")
            variables[var.name] = var

    @staticmethod
    def __load_from_csv(path: Path):
        with open(path) as f:
            lines = f.readlines()

        # lines = [line.strip().rstrip(DELIMITER) for line in lines]
        lines = [line.strip() for line in lines]

        header_section = DatasetLoader.__get_header_section(lines)
        animal_section = DatasetLoader.__get_animal_section(lines, header_section.section_end_index + 1)
        sample_interval_section = DatasetLoader.__get_sample_interval_section(
            lines, animal_section.section_end_index + 1
        )
        group_section = (
            DatasetLoader.__get_group_section(lines, sample_interval_section.section_end_index + 1)
            if sample_interval_section is not None
            else None
        )
        data_section = DatasetLoader.__get_data_section(
            lines,
            group_section.section_end_index + 1 if group_section is not None else animal_section.section_end_index + 1,
        )

        animals: dict[int, Animal] = {}
        variables: dict[str, Variable] = {}

        for line in animal_section.lines[1:]:
            elements = line.split(DELIMITER)
            animal = Animal(
                id=int(elements[1]),
                box=int(elements[0]),
                weight=float(elements[2]),
                text1=elements[3],
                text2=elements[4],
                text3=elements[5] if len(elements) == 6 else "",
            )
            animals[animal.id] = animal

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

        # Add Weight variable
        variables["Weight"] = Variable("Weight", "[g]", "Animal weight")

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

        # find sampling interval
        timedeltas = []
        for index in range(1, 6):
            timedeltas.append(df["DateTime"][index] - df["DateTime"][index - 1])
        timedelta = most_frequent(timedeltas)

        # Sort dataframe
        df.sort_values(by=["DateTime", "Box"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Calculate cumulative values
        DatasetLoader.__add_cumulative_columns(df, "Drink", variables)
        DatasetLoader.__add_cumulative_columns(df, "Feed", variables)

        start_date_time = df["DateTime"][0]
        df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
        df.insert(loc=2, column="Bin", value=(df["Timedelta"] / timedelta).round().astype(int))

        # Add Run column
        df.insert(loc=5, column="Run", value=1)

        # Add Weight column
        if "Weight" not in df.columns:
            df.insert(loc=6, column="Weight", value=df["Animal"])
            weights = {}
            for animal in animals.values():
                weights[animal.id] = animal.weight
            df = df.replace({"Weight": weights})

        # convert categorical types
        df = df.astype({
            "Bin": "category",
            "Run": "category",
            "Weight": "float",
        })

        # Sort variables by name
        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        name = header_section.lines[0].split(DELIMITER)[0]
        description = header_section.lines[0].split(DELIMITER)[1]
        version = header_section.lines[1].split(DELIMITER)[1]

        buf = StringIO()
        df.info(buf=buf)
        meta = {
            "Name": name,
            "Description": description,
            "Version": version,
            "Path": str(path),
            "Animals": [v.get_dict() for i, (k, v) in enumerate(animals.items())],
            "Variables": [v.get_dict() for i, (k, v) in enumerate(variables.items())],
            "Sampling Interval": str(timedelta),
            "Data": [buf.getvalue()],
        }

        return Dataset(
            name=name,
            path=str(path),
            meta=meta,
            animals=animals,
            variables=variables,
            df=df,
            sampling_interval=timedelta,
        )


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = DatasetLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    # dataset = DatasetLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    dataset = DatasetLoader.load("C:\\Users\\anton\\Downloads\\2023-05-24_Test Sample Flow 0.5_90 s per box.csv")
    print(timeit.default_timer() - tic)
