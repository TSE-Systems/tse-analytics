"""Tests for the IntelliCage transitions.processor module."""

import matplotlib
import pandas as pd
import pytest
from tse_analytics.modules.intellicage.toolbox.transitions.processor import (
    IntelliCageTransitionsResult,
    get_intellicage_transitions_result,
)

matplotlib.use("Agg")

_MATRIX_KEYS = {"Observed", "Expected", "Chi-Square", "P-Values", "Ratio"}


@pytest.fixture
def visits_df():
    """A single animal walking a repeating corner sequence over time."""
    sequence = [1, 2, 1, 2, 3, 1, 2, 3, 4, 1] * 4  # 40 visits, includes self-transitions (…1,1…? no)
    rows = [
        {"Animal": "A1", "Timedelta": pd.Timedelta(minutes=i), "Corner": corner} for i, corner in enumerate(sequence)
    ]
    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Corner"] = df["Corner"].astype("UInt8")
    return df


def test_returns_per_animal_matrices(visits_df):
    result = get_intellicage_transitions_result(visits_df, figsize=(6.0, 4.0))

    assert isinstance(result, IntelliCageTransitionsResult)
    assert "A1" in result.matrices
    assert set(result.matrices["A1"]) == _MATRIX_KEYS
    # Per-animal heatmaps are embedded as base64 <img> under the analysis header.
    assert "Chi-Square Analysis of Corner Transitions" in result.report
    assert "<img" in result.report

    observed = result.matrices["A1"]["Observed"]
    # Observed transition matrix is square over the visited corner set.
    assert list(observed.index) == list(observed.columns)


def test_exclude_diagonal_removes_self_transitions(visits_df):
    # Inject a self-transition (corner 4 -> 4) so include_diagonal matters.
    extra = pd.DataFrame([
        {"Animal": "A1", "Timedelta": pd.Timedelta(minutes=100), "Corner": 4},
        {"Animal": "A1", "Timedelta": pd.Timedelta(minutes=101), "Corner": 4},
    ]).astype({"Corner": "UInt8"})
    df = pd.concat([visits_df, extra], ignore_index=True)
    df["Animal"] = df["Animal"].astype("category")

    with_diag = get_intellicage_transitions_result(df, include_diagonal=True)
    without_diag = get_intellicage_transitions_result(df, include_diagonal=False)

    assert with_diag.matrices["A1"]["Observed"].to_numpy().diagonal().sum() > 0
    assert without_diag.matrices["A1"]["Observed"].to_numpy().diagonal().sum() == 0


def test_empty_input_yields_no_matrices():
    empty = pd.DataFrame({
        "Animal": pd.Series([], dtype="category"),
        "Timedelta": pd.Series([], dtype="timedelta64[ns]"),
        "Corner": pd.Series([], dtype="UInt8"),
    })
    result = get_intellicage_transitions_result(empty)
    assert result.matrices == {}
