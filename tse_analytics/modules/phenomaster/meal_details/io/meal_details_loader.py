from pathlib import Path

import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails

DELIMITER = ";"
DECIMAL = "."


class MealDetailsLoader:
    @staticmethod
    def load(filename: str, dataset: Dataset) -> MealDetails | None:
        path = Path(filename)
        if path.is_file() and path.suffix.lower() == ".csv":
            return MealDetailsLoader.__load_from_csv(path, dataset)
        return None

    @staticmethod
    def __add_cumulative_columns(df: pd.DataFrame, origin_name: str, variables: dict[str, Variable]):
        cols = [col for col in df.columns if origin_name in col]
        for col in cols:
            cumulative_col_name = col + "C"
            df[cumulative_col_name] = df.groupby("Box", observed=False)[col].transform(pd.Series.cumsum)
            var = Variable(name=cumulative_col_name, unit=variables[col].unit, description=f"{col} (cumulative)")
            variables[var.name] = var

    @staticmethod
    def __load_from_csv(path: Path, dataset: Dataset):
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

        raw_df = pd.read_csv(
            path,
            delimiter=DELIMITER,
            decimal=DECIMAL,
            skiprows=header_line_number,  # Skip header line
            parse_dates={"DateTime": ["Date", "Time"]},
            encoding="ISO-8859-1",
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

        # Build new dataframe
        new_columns = ["DateTime", "Animal", "Box"]
        variables: dict[str, Variable] = {}
        if drink1_present:
            new_columns.append("Drink1")
            variables["Drink1"] = Variable(name="Drink1", unit="[ml]", description="")
        if feed1_present:
            new_columns.append("Feed1")
            variables["Feed1"] = Variable(name="Feed1", unit="[g]", description="")
        if drink2_present:
            new_columns.append("Drink2")
            variables["Drink2"] = Variable(name="Drink2", unit="[ml]", description="")
        if feed2_present:
            new_columns.append("Feed2")
            variables["Feed2"] = Variable(name="Feed2", unit="[g]", description="")
        if weight_present:
            new_columns.append("Weight")
            variables["Weight"] = Variable(name="Weight", unit="[g]", description="")

        new_df = pd.DataFrame(columns=new_columns)

        box_to_animal_map = {}
        for animal in dataset.animals.values():
            box_to_animal_map[animal.box] = animal.id

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

            new_df = pd.concat([new_df, box_df], ignore_index=True)

        new_df = new_df.sort_values(["Box", "DateTime"])
        new_df.reset_index(drop=True, inplace=True)

        # convert categorical types
        new_df = new_df.astype({
            "Animal": "category",
            "Box": "category",
        })

        # Calculate cumulative values
        if drink1_present:
            MealDetailsLoader.__add_cumulative_columns(new_df, "Drink1", variables)
        if feed1_present:
            MealDetailsLoader.__add_cumulative_columns(new_df, "Feed1", variables)
        if drink2_present:
            MealDetailsLoader.__add_cumulative_columns(new_df, "Drink2", variables)
        if feed2_present:
            MealDetailsLoader.__add_cumulative_columns(new_df, "Feed2", variables)

        # Calo Details sampling interval
        sampling_interval = new_df.iloc[1].at["DateTime"] - new_df.iloc[0].at["DateTime"]

        meal_details = MealDetails(
            dataset,
            f"Meal Details [Interval: {str(sampling_interval)}]",
            str(path),
            variables,
            new_df,
            sampling_interval,
        )
        return meal_details


if __name__ == "__main__":
    import timeit

    tic = timeit.default_timer()
    # dataset = CaloDetailsLoader.load("C:\\Data\\tse-analytics\\20221018_ANIPHY test new logiciel PM_CalR.csv")
    # dataset = CaloDetailsLoader.load("C:\\Users\\anton\\OneDrive\\Desktop\\20221018_ANIPHY test new logiciel PM.csv")
    print(timeit.default_timer() - tic)
