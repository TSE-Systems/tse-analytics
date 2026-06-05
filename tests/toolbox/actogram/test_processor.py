"""Tests for tse_analytics.toolbox.actogram.processor."""

from unittest.mock import patch

import matplotlib
import numpy as np
import pandas as pd
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Animal, Variable
from tse_analytics.toolbox.actogram.processor import dataframe_to_actogram, get_actogram_result

matplotlib.use("Agg")


def _activity_variable() -> Variable:
    return Variable(
        name="Activity",
        unit="counts",
        description="Activity counts",
        type="float",
        aggregation=Aggregation.SUM,
        remove_outliers=False,
    )


def _make_dataset(df: pd.DataFrame, animal_ids: list[str]) -> Dataset:
    """Build a Dataset that keeps the default factors (incl. LightCycle)."""
    animals = {aid: Animal(id=aid, properties={}) for aid in animal_ids}
    metadata = {
        "name": "Actogram Dataset",
        "description": "Actogram test dataset",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-04 00:00:00",
    }
    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(
            name="Actogram Dataset",
            description="Actogram test dataset",
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
    """Hourly DataFrame for the given animals/days; activity_fn(animal_id, hour, day)."""
    base_time = pd.Timestamp("2024-01-01 00:00:00")
    rows = []
    for i in range(days * 24):
        dt = base_time + i * pd.Timedelta("1h")
        for aid in animal_ids:
            rows.append({
                "Animal": aid,
                "DateTime": dt,
                "Activity": float(activity_fn(aid, dt.hour, i // 24)),
            })
    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Activity"] = df["Activity"].astype("Float64")
    return df


class TestDataframeToActogram:
    def test_shape_and_values(self):
        # One animal, 2 days, hourly. With bins_per_day=24 the bin index equals the hour,
        # so each cell is exactly the (single) sample for that hour.
        df = _hourly_df(["M1"], days=2, activity_fn=lambda aid, hour, day: hour * (day + 1))
        variable = _activity_variable()

        activity_array, unique_days = dataframe_to_actogram(df, variable, bins_per_day=24)

        assert activity_array.shape == (2, 24)
        assert len(unique_days) == 2
        np.testing.assert_allclose(activity_array[0], np.arange(24))
        np.testing.assert_allclose(activity_array[1], np.arange(24) * 2)

    def test_missing_bins_are_zero(self):
        # Only two samples on a single day -> all other bins stay 0.
        df = pd.DataFrame({
            "DateTime": pd.to_datetime(["2024-01-01 00:30", "2024-01-01 12:30"]),
            "Activity": pd.array([5.0, 9.0], dtype="Float64"),
        })
        activity_array, unique_days = dataframe_to_actogram(df, _activity_variable(), bins_per_day=24)

        assert activity_array.shape == (1, 24)
        assert activity_array[0, 0] == 5.0
        assert activity_array[0, 12] == 9.0
        assert activity_array[0, [1, 11, 13, 23]].tolist() == [0.0, 0.0, 0.0, 0.0]


class TestGetActogramResult:
    def test_two_animals_returns_image(self):
        df = _hourly_df(
            ["M1", "M2"],
            days=3,
            activity_fn=lambda aid, hour, day: (20 if (hour < 7 or hour >= 19) else 1) + (5 if aid == "M2" else 0),
        )
        dataset = _make_dataset(df, ["M1", "M2"])

        result = get_actogram_result(dataset.datatables["Main"], _activity_variable(), bins_per_hour=2)

        assert "data:image/png;base64," in result.report
        assert "No data" not in result.report

    def test_single_animal_returns_image(self):
        df = _hourly_df(["M1"], days=3, activity_fn=lambda aid, hour, day: 20 if (hour < 7 or hour >= 19) else 1)
        dataset = _make_dataset(df, ["M1"])

        result = get_actogram_result(dataset.datatables["Main"], _activity_variable(), bins_per_hour=4)

        assert "data:image/png;base64," in result.report

    def test_constant_input_does_not_raise(self):
        # All-constant activity -> normalization is skipped (ptp == 0); must still render.
        df = _hourly_df(["M1"], days=2, activity_fn=lambda aid, hour, day: 7.0)
        dataset = _make_dataset(df, ["M1"])

        result = get_actogram_result(dataset.datatables["Main"], _activity_variable(), bins_per_hour=2)

        assert "data:image/png;base64," in result.report

    def test_empty_input_returns_message(self):
        df = pd.DataFrame({
            "Animal": pd.Series([], dtype="category"),
            "DateTime": pd.Series([], dtype="datetime64[ns]"),
            "Activity": pd.Series([], dtype="Float64"),
        })
        dataset = _make_dataset(df, ["M1"])

        result = get_actogram_result(dataset.datatables["Main"], _activity_variable(), bins_per_hour=2)

        assert "No data" in result.report
