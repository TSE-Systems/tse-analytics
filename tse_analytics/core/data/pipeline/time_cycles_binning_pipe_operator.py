import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeCyclesBinningSettings
from tse_analytics.core.data.shared import SplitMode


def process_time_cycles_binning(
    df: pd.DataFrame,
    settings: TimeCyclesBinningSettings,
    binning_operation: BinningOperation,
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
            group_by = ["Animal", "Box", "Bin"] + factor_names
        case SplitMode.FACTOR:
            group_by = [selected_factor_name, "Bin"]
        case SplitMode.RUN:
            group_by = ["Run", "Bin"]
        case _:
            group_by = ["Bin"]

    grouped = df.groupby(group_by, dropna=False, observed=True)

    match binning_operation:
        case BinningOperation.MEAN:
            result = grouped.mean(numeric_only=True)
        case BinningOperation.MEDIAN:
            result = grouped.median(numeric_only=True)
        case _:
            result = grouped.sum(numeric_only=True)

    # the inverse of groupby, reset_index
    result.reset_index(inplace=True)

    return result
