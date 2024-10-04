import pandas as pd

from tse_analytics.core.data.binning import TimeCyclesBinningSettings
from tse_analytics.core.data.shared import SplitMode, Variable

default_columns = ["Timedelta", "Box", "Run"]


def process_time_cycles_binning(
    df: pd.DataFrame,
    settings: TimeCyclesBinningSettings,
    variables: dict[str, Variable],
    split_mode: SplitMode,
    factor_names: list[str],
    selected_factor_name: str,
) -> pd.DataFrame:
    def filter_method(x):
        return "Light" if settings.light_cycle_start <= x.time() < settings.dark_cycle_start else "Dark"

    df["Bin"] = df["DateTime"].apply(filter_method).astype("category")
    df.drop(columns=["DateTime"], inplace=True)

    match split_mode:
        case SplitMode.ANIMAL:
            agg = {
                "Box": "first",
            }
            for factor_name in factor_names:
                agg[factor_name] = "first"
            group_by = ["Animal", "Bin"]
        case SplitMode.FACTOR:
            agg = {}
            group_by = [selected_factor_name, "Bin"]
        case SplitMode.RUN:
            agg = {}
            group_by = ["Run", "Bin"]
        case _:
            agg = {}
            group_by = ["Bin"]

    for variable in variables.values():
        agg[variable.name] = variable.aggregation

    result = df.groupby(group_by, dropna=False, observed=False).agg(agg) if len(agg) != 0 else df

    # the inverse of groupby, reset_index
    result.reset_index(inplace=True)

    return result
