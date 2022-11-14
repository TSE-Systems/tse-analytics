import pandas as pd

from tse_datatools.analysis.binning_params import BinningParams


def apply_time_binning(
    df: pd.DataFrame,
    params: BinningParams
) -> pd.DataFrame:
    # Store initial column order
    cols = df.columns

    result = df.groupby(['Animal', 'Box']).resample(params.timedelta, on='DateTime')

    if params.operation == "mean":
        result = result.mean(numeric_only=True)
    elif params.operation == "median":
        result = result.median(numeric_only=True)
    else:
        result = result.sum(numeric_only=True)

    # the inverse of groupby, reset_index
    result.sort_values(by=['DateTime', 'Box'], inplace=True)
    result = result.reset_index().reindex(cols, axis=1)

    start_date_time = result['DateTime'][0]
    result["Timedelta"] = result['DateTime'] - start_date_time
    result["Bin"] = (result["Timedelta"] / params.timedelta).round().astype(int)
    result['Bin'] = result['Bin'].astype('category')
    return result
