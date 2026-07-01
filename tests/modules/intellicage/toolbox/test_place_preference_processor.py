"""Tests for the IntelliCage place_preference.processor module."""

from types import SimpleNamespace

import matplotlib
import numpy as np
import pandas as pd
import pytest
from tse_analytics.modules.intellicage.toolbox.place_preference.processor import (
    IntelliCagePlacePreferenceResult,
    get_intellicage_place_preference_result,
)

matplotlib.use("Agg")


@pytest.fixture
def visits_df():
    """Synthetic Visits data: A1 strongly prefers corner 1; A2 is uniform."""
    rng = np.random.default_rng(0)
    rows = []
    for animal in ("A1", "A2"):
        probs = [0.7, 0.1, 0.1, 0.1] if animal == "A1" else [0.25, 0.25, 0.25, 0.25]
        for _ in range(60):
            corner = int(rng.choice([1, 2, 3, 4], p=probs))
            rows.append({
                "Animal": animal,
                "Corner": corner,
                "VisitDuration": float(rng.uniform(1.0, 5.0)),
            })
    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Corner"] = df["Corner"].astype("category")
    df["VisitDuration"] = df["VisitDuration"].astype("Float64")
    return df


def test_returns_result_with_populated_frames(visits_df):
    result = get_intellicage_place_preference_result(SimpleNamespace(), visits_df, figsize=(6.0, 4.0))

    assert isinstance(result, IntelliCagePlacePreferenceResult)
    assert isinstance(result.report, str) and result.report.strip()
    assert set(result.visit_counts.index) == {"A1", "A2"}
    assert set(result.visit_results.columns) == {"Animal", "chi2", "p_value", "significant"}


def test_detects_corner_preference(visits_df):
    result = get_intellicage_place_preference_result(SimpleNamespace(), visits_df, figsize=(6.0, 4.0))

    by_animal = result.visit_results.set_index("Animal")
    # A1's skewed distribution is a significant departure from uniform; A2's is not.
    assert bool(by_animal.loc["A1", "significant"])
    assert not bool(by_animal.loc["A2", "significant"])


def test_normalized_counts_sum_to_one_per_animal(visits_df):
    result = get_intellicage_place_preference_result(SimpleNamespace(), visits_df, figsize=(6.0, 4.0))
    row_sums = result.normalized_visit_counts.sum(axis=1)
    assert np.allclose(row_sums.to_numpy(dtype=float), 1.0)
