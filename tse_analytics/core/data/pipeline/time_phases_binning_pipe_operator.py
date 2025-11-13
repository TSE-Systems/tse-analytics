import pandas as pd

from tse_analytics.core.data.binning import TimePhasesBinningSettings
from tse_analytics.core.data.shared import Aggregation, Variable

default_columns = ["Timedelta", "Animal", "Run", "Bin"]


def process_time_phases_binning(
    df: pd.DataFrame,
    settings: TimePhasesBinningSettings,
    variables: dict[str, Variable],
) -> pd.DataFrame:
    settings.time_phases.sort(key=lambda x: x.start_timestamp)

    df["Bin"] = None
    for phase in settings.time_phases:
        df.loc[df["Timedelta"] >= phase.start_timestamp, "Bin"] = phase.name

    df["Bin"] = df["Bin"].astype("category")

    # Drop "DateTime" column
    df.drop(columns=["DateTime"], inplace=True)

    # Sort category names by time
    categories = [item.name for item in settings.time_phases]
    df["Bin"] = df["Bin"].cat.set_categories(categories, ordered=True)

    agg: dict[str, str | Aggregation] = {}
    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category":
                if column in variables:
                    agg[column] = variables[column].aggregation
            else:
                agg[column] = "first"

    result = df.groupby(["Animal", "Bin"], dropna=False, observed=False).aggregate(agg)
    # result.sort_values(by=["Animal", "Bin"], inplace=True)
    result.reset_index(inplace=True)

    return result
