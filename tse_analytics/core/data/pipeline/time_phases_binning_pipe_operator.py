import pandas as pd

from tse_analytics.core.data.binning import TimePhasesBinningSettings
from tse_analytics.core.data.shared import SplitMode, Variable

default_columns = ["Timedelta", "Box", "Run"]


def process_time_phases_binning(
    df: pd.DataFrame,
    settings: TimePhasesBinningSettings,
    variables: dict[str, Variable],
    split_mode: SplitMode,
    factor_names: list[str],
    selected_factor_name: str,
) -> pd.DataFrame:
    settings.time_phases.sort(key=lambda x: x.start_timestamp)

    df["Bin"] = None
    for phase in settings.time_phases:
        df.loc[df["Timedelta"] >= phase.start_timestamp, "Bin"] = phase.name

    df["Bin"] = df["Bin"].astype("category")
    df.drop(columns=["DateTime"], inplace=True)

    # Sort category names by time
    categories = [item.name for item in settings.time_phases]
    df["Bin"] = df["Bin"].cat.set_categories(categories, ordered=True)

    match split_mode:
        case SplitMode.ANIMAL:
            agg = {
                "Box": "first",
                "Run": "first",
            }
            group_by = ["Animal", "Bin"] + factor_names
        case SplitMode.FACTOR:
            agg = {
                "Box": "first",
                "Run": "first",
            }
            group_by = [selected_factor_name, "Bin"]
        case SplitMode.RUN:
            agg = {
                "Box": "first",
            }
            group_by = ["Run", "Bin"]
        case _:
            agg = {
                "Box": "first",
                "Run": "first",
            }
            group_by = ["Bin"]

    for variable in variables.values():
        agg[variable.name] = variable.aggregation

    result = df.groupby(group_by, dropna=False, observed=False).agg(agg)

    # the inverse of groupby, reset_index
    result.reset_index(inplace=True)

    return result
