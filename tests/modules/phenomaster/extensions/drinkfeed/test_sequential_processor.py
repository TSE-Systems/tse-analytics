"""Unit tests for the DrinkFeed sequential processor wide-episodes reshape."""

import pandas as pd
import pytest
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.modules.phenomaster.extensions.drinkfeed.sequential_processor import _reshape_episodes_to_wide

_METRICS = ["Duration[minutes]", "Interval[minutes]", "Quantity", "Quantity[kcal]", "Rate"]


def _make_long_episodes_df() -> pd.DataFrame:
    """A minimal long, per-episode frame like ``process_drinkfeed_sequences`` produces."""
    rows = [
        # DateTime, Timedelta[min], Animal, Sensor, Duration[min], Interval[min], Quantity, Quantity[kcal], Rate
        ("2024-01-01 08:01:00", 1, "A1", "Drink1", 0.5, 4.0, 0.12, 0.0, 0.24),
        ("2024-01-01 08:05:00", 5, "A1", "Feed1", 1.0, 3.0, 0.30, 0.9, 0.30),
        ("2024-01-01 08:12:00", 12, "A1", "Drink1", 0.4, 11.0, 0.09, 0.0, 0.225),
    ]
    df = pd.DataFrame(rows, columns=["DateTime", "Timedelta", "Animal", "Sensor", *_METRICS])
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"], unit="m")
    df["Animal"] = df["Animal"].astype("category")
    df["Sensor"] = df["Sensor"].astype("category")
    for col in _METRICS:
        df[col] = df[col].astype("Float64")
    return df


def test_reshape_episodes_to_wide_columns_and_values():
    long_df = _make_long_episodes_df()
    wide, variables = _reshape_episodes_to_wide(long_df)

    # One row per episode; no Sensor column; id columns retained.
    assert len(wide) == len(long_df)
    assert "Sensor" not in wide.columns
    assert {"DateTime", "Timedelta", "Animal"} <= set(wide.columns)

    # Per-sensor metric columns (and their Variables) exist for both sensors.
    for sensor in ("Drink1", "Feed1"):
        for metric in _METRICS:
            assert f"{sensor}{metric}" in wide.columns
            assert f"{sensor}{metric}" in variables

    # Values land in the row's own sensor column; other sensors are <NA>.
    assert wide["Drink1Quantity"].iloc[0] == pytest.approx(0.12)
    assert pd.isna(wide["Feed1Quantity"].iloc[0])
    assert wide["Feed1Quantity"].iloc[1] == pytest.approx(0.30)
    assert pd.isna(wide["Drink1Quantity"].iloc[1])
    assert wide["Drink1Quantity"].iloc[2] == pytest.approx(0.09)


def test_reshape_episodes_to_wide_units_and_aggregations():
    _, variables = _reshape_episodes_to_wide(_make_long_episodes_df())

    # Units resolved per sensor.
    assert variables["Drink1Quantity"].unit == "ml"
    assert variables["Feed1Quantity"].unit == "g"
    assert variables["Drink1Rate"].unit == "ml/min"
    assert variables["Feed1Rate"].unit == "g/min"
    assert variables["Feed1Quantity[kcal]"].unit == "kcal"

    # Aggregations preserved per metric.
    assert variables["Drink1Quantity"].aggregation == Aggregation.SUM
    assert variables["Drink1Duration[minutes]"].aggregation == Aggregation.SUM
    assert variables["Drink1Interval[minutes]"].aggregation == Aggregation.MEAN
    assert variables["Drink1Rate"].aggregation == Aggregation.MEAN


def test_reshape_episodes_to_wide_empty():
    empty_df = _make_long_episodes_df().iloc[0:0]
    wide, variables = _reshape_episodes_to_wide(empty_df)

    assert variables == {}
    assert list(wide.columns) == ["DateTime", "Timedelta", "Animal"]
    assert len(wide) == 0
