import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimePhasesBinningSettings
from tse_analytics.core.data.shared import SplitMode


def process_time_phases_binning(
    df: pd.DataFrame,
    settings: TimePhasesBinningSettings,
    binning_operation: BinningOperation,
    split_mode: SplitMode,
    factor_names: list[str],
    selected_factor_name: str | None,
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
            group_by = ["Animal", "Box", "Bin"] + factor_names
        case SplitMode.FACTOR:
            group_by = [selected_factor_name, "Bin"]
        case SplitMode.RUN:
            group_by = ["Run", "Bin"]
        case SplitMode.TOTAL:
            group_by = ["Bin"]

    grouped = df.groupby(group_by, dropna=False, observed=True)

    match binning_operation:
        case BinningOperation.MEAN:
            result = grouped.mean(numeric_only=True)
        case BinningOperation.MEDIAN:
            result = grouped.median(numeric_only=True)
        case BinningOperation.SUM:
            result = grouped.sum(numeric_only=True)

    # the inverse of groupby, reset_index
    result = result.reset_index()

    return result
