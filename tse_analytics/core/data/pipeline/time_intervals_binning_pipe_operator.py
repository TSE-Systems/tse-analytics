import pandas as pd

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import Variable

default_columns = ["DateTime", "Timedelta", "Animal", "Run"]


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
        "Run": "first",
    }
    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category" and column in variables:
                agg[column] = variables[column].aggregation
            else:
                agg[column] = "first"

    if calculate_errors is not None:
        var_name = list(variables.values())[0].name
        df["Error"] = df[var_name]
        agg["Error"] = calculate_errors

    result = df.groupby("Animal", dropna=False, observed=False)
    result = result.resample(timedelta, on="Timedelta", origin="start").aggregate(agg)

    result = result[result["Run"].notna()]

    result.sort_values(by="DateTime", inplace=True)
    result.reset_index(inplace=True, drop=False)

    # Get unique runs numbers
    runs = result["Run"].unique().tolist()

    # Reassign timedeltas
    for run in runs:
        # Get start timestamp per run
        start_date_time = result[result["Run"] == run]["DateTime"].iloc[0]
        result.loc[result["Run"] == run, "Timedelta"] = result["DateTime"] - start_date_time

    # Reassign bins numbers
    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)

    result.sort_values(by="Bin", inplace=True)
    result.reset_index(inplace=True, drop=True)

    return result
