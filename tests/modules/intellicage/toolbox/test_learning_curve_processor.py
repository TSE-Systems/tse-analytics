"""Tests for the IntelliCage learning_curve.processor module."""

from types import SimpleNamespace

import matplotlib
import numpy as np
import pandas as pd
import pytest
from tse_analytics.core.data.shared import ByAnimalConfig, Factor, FactorLevel, FactorRole
from tse_analytics.modules.intellicage.toolbox.learning_curve.processor import (
    BIN_MODE_TIME,
    BIN_MODE_VISIT,
    METRIC_CORRECT_VISITS,
    METRIC_LICKS_PER_VISIT,
    METRIC_NOSEPOKE_ERROR_RATE,
    METRIC_PLACE_ERROR_RATE,
    IntelliCageLearningCurveResult,
    get_intellicage_learning_curve_result,
)

matplotlib.use("Agg")

ANIMALS = ["M1", "M2", "M3", "M4"]
VISITS_PER_ANIMAL = 200
CORNER_CATEGORIES = ["Incorrect", "Neutral", "Correct"]


@pytest.fixture
def visits_df():
    """Synthetic IntelliCage Visits dataframe where place accuracy improves over time.

    Each animal performs ``VISITS_PER_ANIMAL`` visits spread across 8 days. The
    probability of a "Correct" corner choice ramps from ~0.2 up to ~0.9, so the
    %-correct learning curve has a clearly positive slope.
    """
    rng = np.random.default_rng(42)
    rows = []
    for animal in ANIMALS:
        for i in range(VISITS_PER_ANIMAL):
            progress = i / (VISITS_PER_ANIMAL - 1)  # 0.0 -> 1.0
            p_correct = 0.2 + 0.7 * progress
            correct = rng.random() < p_correct
            condition = "Correct" if correct else rng.choice(["Incorrect", "Neutral"])
            rows.append({
                "Animal": animal,
                "Timedelta": pd.Timedelta(days=8) * progress,
                "Group": "Control" if animal in ("M1", "M2") else "Treatment",
                "CornerCondition": condition,
                "PlaceError": 0 if correct else 1,
                "SideErrors": int(rng.integers(0, 2)) if not correct else 0,
                "NosepokesNumber": int(rng.integers(1, 5)),
                "LicksNumber": int(rng.integers(0, 20)),
            })

    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Group"] = df["Group"].astype("category")
    df["CornerCondition"] = pd.Categorical(df["CornerCondition"], categories=CORNER_CATEGORIES, ordered=True)
    df["PlaceError"] = df["PlaceError"].astype("Int64")
    df["SideErrors"] = df["SideErrors"].astype("Int64")
    df["NosepokesNumber"] = df["NosepokesNumber"].astype("Int64")
    df["LicksNumber"] = df["LicksNumber"].astype("Int64")
    return df


@pytest.fixture
def dataset_stub():
    """Minimal stand-in exposing the ``.factors`` mapping the processor reads."""
    animal_factor = Factor(name="Animal", config=ByAnimalConfig(), role=FactorRole.BETWEEN_SUBJECT, levels={})
    group_factor = Factor(
        name="Group",
        config=ByAnimalConfig(),
        role=FactorRole.BETWEEN_SUBJECT,
        levels={
            "Control": FactorLevel(name="Control", color="#FF0000", animal_ids=["M1", "M2"]),
            "Treatment": FactorLevel(name="Treatment", color="#00FF00", animal_ids=["M3", "M4"]),
        },
    )
    return SimpleNamespace(factors={"Animal": animal_factor, "Group": group_factor})


@pytest.mark.parametrize(
    "metric",
    [METRIC_CORRECT_VISITS, METRIC_PLACE_ERROR_RATE, METRIC_NOSEPOKE_ERROR_RATE, METRIC_LICKS_PER_VISIT],
)
@pytest.mark.parametrize("bin_mode", [BIN_MODE_TIME, BIN_MODE_VISIT])
def test_returns_result_for_each_metric_and_bin_mode(visits_df, dataset_stub, metric, bin_mode):
    bin_size = 24 if bin_mode == BIN_MODE_TIME else 50
    result = get_intellicage_learning_curve_result(
        dataset=dataset_stub,
        df=visits_df,
        metric=metric,
        bin_mode=bin_mode,
        bin_size=bin_size,
        group_by="Animal",
        figsize=(8, 6),
    )

    assert isinstance(result, IntelliCageLearningCurveResult)
    assert isinstance(result.report, str) and result.report
    assert set(result.curve_data.columns) >= {"Animal", "Bin", "Metric"}
    assert not result.curve_data.empty
    assert set(result.summary.columns) >= {"Animal", "Start", "End", "Change", "Slope", "Bins"}
    assert len(result.summary) == len(ANIMALS)


def test_correct_visits_slope_is_positive(visits_df, dataset_stub):
    """A learning dataset should yield an increasing %-correct curve (positive slope)."""
    result = get_intellicage_learning_curve_result(
        dataset=dataset_stub,
        df=visits_df,
        metric=METRIC_CORRECT_VISITS,
        bin_mode=BIN_MODE_VISIT,
        bin_size=50,
        group_by="Animal",
        figsize=(8, 6),
    )

    assert result.summary["Slope"].mean() > 0
    assert (result.summary["Change"] > 0).all()


def test_grouping_by_factor_includes_group_column(visits_df, dataset_stub):
    result = get_intellicage_learning_curve_result(
        dataset=dataset_stub,
        df=visits_df,
        metric=METRIC_CORRECT_VISITS,
        bin_mode=BIN_MODE_TIME,
        bin_size=24,
        group_by="Group",
        figsize=(8, 6),
    )

    assert "Group" in result.curve_data.columns
    assert "Group" in result.summary.columns
    assert set(result.summary["Group"].unique()) == {"Control", "Treatment"}
