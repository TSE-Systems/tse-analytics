import pandas as pd

from tse_analytics.core.data.shared import Variable


def group_by_columns(df: pd.DataFrame, group_by: list[str], variables: dict[str, Variable]) -> pd.DataFrame:
    aggregation = {}

    if "DateTime" in df.columns:
        aggregation["DateTime"] = "first"

    if "Timedelta" in df.columns:
        aggregation["Timedelta"] = "first"

    # TODO: use means only when aggregating in split modes!
    for variable in variables.values():
        aggregation[variable.name] = "mean"

    result = df.groupby(group_by, dropna=False, observed=False).aggregate(aggregation)
    result.reset_index(inplace=True)

    return result
