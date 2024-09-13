import pandas as pd

from tse_analytics.modules.phenomaster.actimot.actimot_settings import ActimotSettings
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails


def process_actimot_data(actimot_details: ActimotDetails, actimot_settings: ActimotSettings):
    box_to_animal_map = {}
    for animal in actimot_details.dataset.animals.values():
        box_to_animal_map[animal.box] = animal.id

    df = actimot_details.raw_df.copy()

    group_by = ["Animal", "Box"]
    grouped = df.groupby(group_by, dropna=False, observed=False)

    timedelta = pd.Timedelta(
        hours=0,
        minutes=0,
        seconds=1,
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
    # result = result.astype({"Bin": "category"})

    return result
