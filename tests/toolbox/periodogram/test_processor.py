"""Tests for tse_analytics.toolbox.periodogram.processor."""

import math
from unittest.mock import patch

import matplotlib
import pandas as pd
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Animal, Variable
from tse_analytics.toolbox.periodogram.processor import get_periodogram_result

matplotlib.use("Agg")


def _activity_variable() -> Variable:
    return Variable(
        name="Activity",
        unit="counts",
        description="Activity counts",
        type="float",
        aggregation=Aggregation.MEAN,
        remove_outliers=False,
    )


def _make_dataset(df: pd.DataFrame, animal_ids: list[str]) -> Dataset:
    """Build a Dataset that keeps the default factors (incl. Animal/LightCycle)."""
    animals = {aid: Animal(id=aid, properties={}) for aid in animal_ids}
    metadata = {
        "name": "Periodogram Dataset",
        "description": "Periodogram test dataset",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-07 00:00:00",
    }
    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(
            name="Periodogram Dataset",
            description="Periodogram test dataset",
            dataset_type="PhenoMaster",
            metadata=metadata,
            animals=animals,
        )
        datatable = Datatable(
            dataset=dataset,
            name="Main",
            description="Main datatable",
            variables={"Activity": _activity_variable()},
            df=df,
            metadata={},
        )
        dataset.datatables["Main"] = datatable
    return dataset


def _hourly_df(animal_ids: list[str], days: int, activity_fn) -> pd.DataFrame:
    """Hourly DataFrame for the given animals/days; activity_fn(animal_id, hour_index)."""
    base_time = pd.Timestamp("2024-01-01 00:00:00")
    rows = []
    for i in range(days * 24):
        dt = base_time + i * pd.Timedelta("1h")
        for aid in animal_ids:
            rows.append({
                "Animal": aid,
                "DateTime": dt,
                "Activity": float(activity_fn(aid, i)),
            })
    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Activity"] = df["Activity"].astype("Float64")
    return df


def _circadian(_aid: str, hour_index: int) -> float:
    """Clean 24 h sinusoid."""
    return 10.0 + 5.0 * math.sin(2.0 * math.pi * hour_index / 24.0)


class TestGetPeriodogramResult:
    def test_returns_image(self):
        df = _hourly_df(["M1"], days=5, activity_fn=_circadian)
        dataset = _make_dataset(df, ["M1"])

        result = get_periodogram_result(dataset.datatables["Main"], _activity_variable(), "Animal")

        assert "data:image/png;base64," in result.report

    def test_detects_circadian_period(self):
        # A clean 24 h sinusoid must yield a dominant period close to 24 h. This is the
        # regression guard for the old bug that collapsed the series to one row per group.
        df = _hourly_df(["M1"], days=6, activity_fn=_circadian)
        dataset = _make_dataset(df, ["M1"])

        result = get_periodogram_result(dataset.datatables["Main"], _activity_variable(), "Animal")

        assert abs(result.dominant_periods["M1"] - 24.0) < 2.0

    def test_two_animals_overlay(self):
        df = _hourly_df(
            ["M1", "M2"],
            days=5,
            activity_fn=lambda aid, i: _circadian(aid, i) + (2.0 if aid == "M2" else 0.0),
        )
        dataset = _make_dataset(df, ["M1", "M2"])

        result = get_periodogram_result(dataset.datatables["Main"], _activity_variable(), "Animal")

        assert "data:image/png;base64," in result.report
        assert set(result.dominant_periods.keys()) == {"M1", "M2"}

    def test_constant_input_does_not_raise(self):
        # Constant series -> Lomb-Scargle is undefined; must not divide by zero.
        df = _hourly_df(["M1"], days=3, activity_fn=lambda aid, i: 7.0)
        dataset = _make_dataset(df, ["M1"])

        result = get_periodogram_result(dataset.datatables["Main"], _activity_variable(), "Animal")

        assert "Not enough valid data" in result.report

    def test_empty_input_returns_message(self):
        df = pd.DataFrame({
            "Animal": pd.Series([], dtype="category"),
            "DateTime": pd.Series([], dtype="datetime64[ns]"),
            "Activity": pd.Series([], dtype="Float64"),
        })
        dataset = _make_dataset(df, ["M1"])

        result = get_periodogram_result(dataset.datatables["Main"], _activity_variable(), "Animal")

        assert "No data" in result.report
