import pandas as pd

from tse_analytics.core.data.binning import TimeCyclesBinningSettings
from tse_analytics.core.data.shared import Variable

default_columns = ["Timedelta", "Animal", "Run", "Bin"]


def process_time_cycles_binning(
    df: pd.DataFrame,
    settings: TimeCyclesBinningSettings,
    variables: dict[str, Variable],
) -> pd.DataFrame:
    def filter_method(x):
        return "Light" if settings.light_cycle_start <= x.time() < settings.dark_cycle_start else "Dark"

    df["Bin"] = df["DateTime"].apply(filter_method).astype("category")

    # Drop "DateTime" column
    df.drop(columns=["DateTime"], inplace=True)

    agg = {}
    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category":
                agg[column] = variables[column].aggregation
            else:
                agg[column] = "first"

    if len(agg) == 0:
        result = df.groupby(["Animal", "Bin"], dropna=False, observed=False).aggregate(
            EntriesInBin=("Bin", "size"),
        )
    else:
        result = df.groupby(["Animal", "Bin"], dropna=False, observed=False).aggregate(agg)
    # result.sort_values(by=["Animal", "Bin"], inplace=True)
    result.reset_index(inplace=True)

    return result
