import pandas as pd

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import Variable

default_columns = ["Animal", "Timedelta", "DateTime", "Run"]


def process_time_interval_binning(
    df: pd.DataFrame,
    settings: TimeIntervalsBinningSettings,
    variables: dict[str, Variable],
    calculate_errors: str | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df

    timedelta = pd.Timedelta(f"{settings.delta}{settings.unit}")

    agg = {
        "DateTime": "first",
    }

    include_runs = "Run" in df.columns
    if include_runs:
        agg["Run"] = "first"

    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category":
                if column in variables:
                    agg[column] = variables[column].aggregation
            else:
                # Include categorical data fields
                agg[column] = "first"


    if calculate_errors is not None:
        var_name = list(variables.values())[0].name
        df["Error"] = df[var_name]
        agg["Error"] = calculate_errors

    result = df.groupby("Animal", dropna=False, observed=False)
    result = result.resample(timedelta, on="Timedelta", origin="start").aggregate(agg)

    result = result[result["DateTime"].notna()]

    # result.sort_values(by="Timedelta", inplace=True)
    result.reset_index(inplace=True, drop=False)

    # Reassign bins numbers
    result.insert(loc=0, column="Bin", value=(result["Timedelta"] / timedelta).round().astype(int))

    result.sort_values(by="Bin", inplace=True)
    result.reset_index(inplace=True, drop=True)

    if include_runs:
        result = result.astype({
            "Run": int,
        })

    return result
