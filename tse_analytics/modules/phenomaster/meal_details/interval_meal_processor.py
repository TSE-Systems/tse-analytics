import pandas as pd

from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


def process_meal_intervals(
    meal_details: MealDetails, meal_details_settings: MealDetailsSettings, diets_dict: dict[int, float]
):
    box_to_animal_map = {}
    for animal in meal_details.dataset.animals.values():
        box_to_animal_map[animal.box] = animal.id

    df = meal_details.raw_df.copy()

    dropped_columns = []
    if "Drink1C" in df.columns:
        dropped_columns.append("Drink1C")
    if "Feed1C" in df.columns:
        dropped_columns.append("Feed1C")
    if "Drink2C" in df.columns:
        dropped_columns.append("Drink2C")
    if "Feed2C" in df.columns:
        dropped_columns.append("Feed2C")
    df.drop(dropped_columns, axis="columns", inplace=True)

    group_by = ["Animal", "Box"]
    grouped = df.groupby(group_by, dropna=False, observed=False)

    timedelta = pd.Timedelta(
        hours=meal_details_settings.fixed_interval.hour,
        minutes=meal_details_settings.fixed_interval.minute,
        seconds=meal_details_settings.fixed_interval.second,
    )
    resampler = grouped.resample(timedelta, on="DateTime", origin="start")
    result = resampler.sum(numeric_only=True)

    sort_by = ["DateTime", "Animal"]
    result.sort_values(by=sort_by, inplace=True)

    # the inverse of groupby, reset_index
    result = result.reset_index()

    start_date_time = result["DateTime"][0]
    result["Timedelta"] = result["DateTime"] - start_date_time

    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    result = result.astype({"Bin": "category"})

    # __add_caloric_column(result, "Drink1", diets_dict)
    __add_caloric_column(result, "Feed1", diets_dict)
    # __add_caloric_column(result, "Drink2", diets_dict)
    __add_caloric_column(result, "Feed2", diets_dict)

    return result


def __add_caloric_column(df: pd.DataFrame, origin_column: str, diets_dict: dict[int, float]) -> pd.DataFrame:
    if origin_column in df.columns:
        df.insert(df.columns.get_loc(origin_column) + 1, f"{origin_column}-kcal", df["Box"].astype(int))
        df.replace({f"{origin_column}-kcal": diets_dict}, inplace=True)
        df[f"{origin_column}-kcal"] = df[f"{origin_column}-kcal"] * df[origin_column]
    return df
