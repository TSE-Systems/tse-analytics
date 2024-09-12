import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import SplitMode


def process_time_interval_binning(
    df: pd.DataFrame,
    settings: TimeIntervalsBinningSettings,
    binning_operation: BinningOperation,
    split_mode: SplitMode,
    factor_names: list[str],
    selected_factor_name: str | None,
) -> pd.DataFrame:
    match split_mode:
        case SplitMode.ANIMAL:
            group_by = ["Animal", "Box"] + factor_names
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case SplitMode.FACTOR:
            group_by = [selected_factor_name]
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case SplitMode.RUN:
            group_by = ["Run"]
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case _:
            grouped = df

    timedelta = pd.Timedelta(f"{settings.delta}{settings.unit}")
    resampler = grouped.resample(timedelta, on="Timedelta", origin="start")

    match binning_operation:
        case BinningOperation.MEAN:
            result = resampler.mean(numeric_only=True)
        case BinningOperation.MEDIAN:
            result = resampler.median(numeric_only=True)
        case _:
            result = resampler.sum(numeric_only=True)

    match split_mode:
        case SplitMode.ANIMAL:
            sort_by = ["Timedelta", "Animal"]
        case SplitMode.FACTOR:
            sort_by = ["Timedelta", selected_factor_name]
        case SplitMode.RUN:
            sort_by = ["Timedelta", "Run"]
        case _:
            sort_by = ["Timedelta"]

    result.sort_values(by=sort_by, inplace=True)

    # the inverse of groupby, reset_index
    result = result.reset_index()

    # start_date_time = result["DateTime"].iloc[0]
    # result["Timedelta"] = result["DateTime"] - start_date_time

    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    result = result.astype({"Bin": "category"})

    return result
