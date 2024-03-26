import pandas as pd

from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


def process_meal_intervals(meal_details: MealDetails, meal_details_settings: MealDetailsSettings):
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

    return result
