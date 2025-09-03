import pandas as pd
from scipy.stats import shapiro, levene


def normality_test(df: pd.DataFrame, variable: str, factor: str, alpha=0.05) -> pd.DataFrame:
    grp = df.groupby(factor, observed=True, sort=False)[variable]
    normality_results = grp.apply(lambda x: shapiro(x))
    result = pd.DataFrame(normality_results.tolist(), index=grp.groups.keys(), columns=["W", "p-value"])
    result["normal"] = result["p-value"] > alpha
    return result


def homoscedasticity_test(df: pd.DataFrame, variable: str, factor: str, alpha=0.05) -> pd.DataFrame:
    grp = df.groupby(factor, observed=True)[variable]
    w, p_value = levene(*grp.apply(list))
    result = pd.DataFrame([
        {
            "W": w,
            "p-value": p_value,
            "equal": p_value > alpha,
        }
    ])
    return result
