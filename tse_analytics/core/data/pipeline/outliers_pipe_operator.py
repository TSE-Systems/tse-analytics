import polars as pl

from tse_analytics.core.data.outliers import OutliersParams


def process_outliers(df: pl.DataFrame, settings: OutliersParams, variables: list[str]) -> pl.DataFrame:
    # Calculate quantiles and IQR
    q1 = df.select(variables).quantile(0.25)
    q3 = df.select(variables).quantile(0.75)
    iqr = q3 - q1

    # Return a boolean array of the rows with (any) non-outlier column values
    # Create a boolean mask to identify outliers
    condition = (df[variables] < (q1 - settings.coefficient * iqr)) | (df[variables] > (q3 + settings.coefficient * iqr))

    # Filter our dataframe based on condition
    result = df[condition]

    return result
