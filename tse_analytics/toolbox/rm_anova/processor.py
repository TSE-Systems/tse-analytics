import pandas as pd
import numpy as np
from scipy import stats
from scipy import linalg


def mauchly_test(data: pd.DataFrame, dv: str, within: str, subject: str):
    """
    Performs Mauchly's Test for Sphericity on a long-format DataFrame.

    This implementation is based on the formulas used in statistical packages like R and SPSS,
    and does not require the 'pingouin' library.

    Args:
        data (pd.DataFrame): The long-format DataFrame.
        dv (str): The name of the column containing the dependent variable.
        within (str): The name of the column containing the within-subject factor (e.g., 'time', 'condition').
        subject (str): The name of the column containing the subject/participant identifier.

    Returns:
        pd.Series: A pandas Series containing the results:
            - 'sphericity': Boolean, True if p > 0.05 (sphericity assumed).
            - 'W': Mauchly's W test statistic.
            - 'chi2': The Chi-Square approximation of W.
            - 'df': Degrees of freedom for the Chi-Square test.
            - 'p-val': The p-value of the test.
            - 'gg': Greenhouse-Geisser epsilon correction.
            - 'hf': Huynh-Feldt epsilon correction.
    """
    # 1. Reshape the data from long to wide format
    try:
        df_wide = data.pivot_table(index=subject, columns=within, values=dv)
    except Exception as e:
        raise ValueError(f"Could not pivot the data. Check column names and data structure. Error: {e}")

    # Drop subjects with any missing data for the within-subject factor
    df_wide = df_wide.dropna()

    # Get dimensions
    n, k = df_wide.shape

    if k < 2:
        print("Mauchly's test is not applicable for less than 2 levels of the within-subject factor.")
        return None

    # Sphericity is always met for k=2 levels
    if k == 2:
        return pd.Series({
            'sphericity': True,
            'W': 1.0,
            'chi2': 0.0,
            'df': 1,
            'p-val': 1.0,
            'gg': 1.0,
            'hf': 1.0
        }, name='Mauchly Test')

    # 2. Calculate the sample covariance matrix S
    S = df_wide.cov().to_numpy()

    # 3. Create an orthonormal contrast matrix C
    # We need a (k x k-1) matrix where columns are orthogonal to each other and to a vector of 1s.
    # A robust way to do this is using the SVD of a matrix with a column of 1s.
    q = np.ones((k, 1))
    U, _, _ = linalg.svd(q)
    C = U[:, 1:]  # The remaining k-1 columns form our orthonormal contrast matrix

    # 4. Transform the covariance matrix
    # M = C' * S * C
    M = C.T @ S @ C

    # 5. Calculate Mauchly's W statistic
    p = k - 1
    det_M = np.linalg.det(M)
    trace_M_div_p = np.trace(M) / p
    W = det_M / (trace_M_div_p ** p)

    # 6. Calculate the Chi-Square approximation and p-value
    # Using the correction factor from Box (1950)
    df = (p * (p + 1) / 2) - 1

    # Box's correction factor for the chi-square approximation
    # This makes the approximation more accurate for small sample sizes
    rho = 1 - (2 * p ** 2 + p + 2) / (6 * p * (n - 1))
    chi2 = -(n - 1) * rho * np.log(W)

    # Some older formulas might use a slightly different correction, but this is standard.
    # A simpler approximation is just -(n-1)*log(W), but Box's is better.

    p_value = stats.chi2.sf(chi2, df)

    # 7. Calculate Greenhouse-Geisser and Huynh-Feldt epsilons
    # Greenhouse-Geisser epsilon (ε_gg)
    # Formula: (tr(S))^2 / ( (k) * tr(S^2) )
    # where tr(S^2) is the sum of all squared elements of S.
    tr_S = np.trace(S)
    tr_S_squared = np.sum(S ** 2)
    epsilon_gg = tr_S ** 2 / (k * tr_S_squared)

    # Huynh-Feldt epsilon (ε_hf)
    # This is a correction on the GG epsilon to make it less conservative.
    # Formula: (n * (k-1) * ε_gg - 2) / ((k-1) * (n - 1 - (k-1) * ε_gg))
    num_hf = n * (k - 1) * epsilon_gg - 2
    den_hf = (k - 1) * (n - 1 - (k - 1) * epsilon_gg)
    epsilon_hf = num_hf / den_hf

    # The HF epsilon can exceed 1.0, in which case it's capped at 1.0
    epsilon_hf = min(epsilon_hf, 1.0)

    # Compile results
    results = pd.Series({
        'sphericity': p_value > 0.05,
        'W': W,
        'chi2': chi2,
        'df': df,
        'p-val': p_value,
        'gg': epsilon_gg,
        'hf': epsilon_hf
    }, name='Mauchly Test')

    return results
