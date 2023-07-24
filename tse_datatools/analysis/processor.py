import pandas as pd


def find_outliers_iqr(df: pd.DataFrame, extreme=False):
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3 - q1
    coef = 3.0 if extreme else 1.5
    outliers = df[((df < (q1 - coef * iqr)) | (df > (q3 + coef * iqr)))]
    return outliers
