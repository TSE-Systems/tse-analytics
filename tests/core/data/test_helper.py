"""Tests for tse_analytics.core.data.helper module."""

import numpy as np
import pandas as pd
from tse_analytics.core.data.helper import (
    normalize_nd_array,
    reassign_df_timedelta_and_bin,
    rename_animal_df,
)
from tse_analytics.core.data.shared import Animal


class TestRenameAnimalDf:
    """Tests for rename_animal_df function."""

    def test_renames_animal_id(self):
        df = pd.DataFrame({"Animal": ["A1", "A1", "A2"], "Value": [1, 2, 3]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(enabled=True, id="A1_renamed", color="#FF0000", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert "A1_renamed" in result["Animal"].values
        assert "A1" not in result["Animal"].values

    def test_preserves_category_dtype(self):
        df = pd.DataFrame({"Animal": ["A1", "A2"]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(enabled=True, id="B1", color="#FF0000", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert result["Animal"].dtype.name == "category"

    def test_does_not_affect_other_animals(self):
        df = pd.DataFrame({"Animal": ["A1", "A2", "A3"], "Value": [1, 2, 3]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(enabled=True, id="B1", color="#FF0000", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert result.loc[1, "Animal"] == "A2"
        assert result.loc[2, "Animal"] == "A3"


class TestReassignDfTimedeltaAndBin:
    """Tests for reassign_df_timedelta_and_bin function."""

    def test_reassigns_timedelta_none_mode(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "DateTime": [base, base + pd.Timedelta("1h"), base + pd.Timedelta("2h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta(0), pd.Timedelta(0)],  # wrong initial values
            "Bin": [0, 0, 0],
        })

        interval = pd.Timedelta("1h")
        result = reassign_df_timedelta_and_bin(df, interval, None)

        assert result["Timedelta"].iloc[0] == pd.Timedelta(0)
        assert result["Timedelta"].iloc[1] == pd.Timedelta("1h")
        assert result["Timedelta"].iloc[2] == pd.Timedelta("2h")

    def test_reassigns_bin_numbers(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "DateTime": [base, base + pd.Timedelta("1h"), base + pd.Timedelta("2h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta("1h"), pd.Timedelta("2h")],
            "Bin": [99, 99, 99],
        })

        interval = pd.Timedelta("1h")
        result = reassign_df_timedelta_and_bin(df, interval, None)

        assert result["Bin"].iloc[0] == 0
        assert result["Bin"].iloc[1] == 1
        assert result["Bin"].iloc[2] == 2

    def test_overlap_mode_per_run_timedelta(self):
        base1 = pd.Timestamp("2024-01-01")
        base2 = pd.Timestamp("2024-01-02")
        df = pd.DataFrame({
            "DateTime": [base1, base1 + pd.Timedelta("1h"), base2, base2 + pd.Timedelta("1h")],
            "Timedelta": [pd.Timedelta(0)] * 4,
            "Bin": [0] * 4,
            "Run": [1, 1, 2, 2],
        })

        interval = pd.Timedelta("1h")
        result = reassign_df_timedelta_and_bin(df, interval, "overlap")

        # Each run starts from 0
        assert result["Timedelta"].iloc[0] == pd.Timedelta(0)
        assert result["Timedelta"].iloc[2] == pd.Timedelta(0)

    def test_none_sampling_interval_skips_bin(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "DateTime": [base, base + pd.Timedelta("1h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta("1h")],
            "Bin": [99, 99],
        })

        result = reassign_df_timedelta_and_bin(df, None, None)
        # Bin should remain unchanged
        assert result["Bin"].iloc[0] == 99


class TestNormalizeNdArray:
    """Tests for normalize_nd_array function."""

    def test_normalizes_to_01_range(self):
        arr = np.array([0.0, 5.0, 10.0])
        result = normalize_nd_array(arr)

        assert result[0] == 0.0
        assert result[1] == 0.5
        assert result[2] == 1.0

    def test_handles_negative_values(self):
        arr = np.array([-10.0, 0.0, 10.0])
        result = normalize_nd_array(arr)

        assert result[0] == 0.0
        assert result[1] == 0.5
        assert result[2] == 1.0

    def test_output_range(self):
        arr = np.array([3.0, 7.0, 1.0, 9.0, 5.0])
        result = normalize_nd_array(arr)

        assert np.min(result) == 0.0
        assert np.max(result) == 1.0
