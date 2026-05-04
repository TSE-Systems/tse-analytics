"""Tests for tse_analytics.core.data.helper module."""

import numpy as np
import pandas as pd
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.utils.data import normalize_nd_array, reassign_df_timedelta, rename_animal_df


class TestRenameAnimalDf:
    """Tests for rename_animal_df function."""

    def test_renames_animal_id(self):
        df = pd.DataFrame({"Animal": ["A1", "A1", "A2"], "Value": [1, 2, 3]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(id="A1_renamed", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert "A1_renamed" in result["Animal"].values
        assert "A1" not in result["Animal"].values

    def test_preserves_category_dtype(self):
        df = pd.DataFrame({"Animal": ["A1", "A2"]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(id="B1", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert result["Animal"].dtype.name == "category"

    def test_does_not_affect_other_animals(self):
        df = pd.DataFrame({"Animal": ["A1", "A2", "A3"], "Value": [1, 2, 3]})
        df["Animal"] = df["Animal"].astype("category")

        animal = Animal(id="B1", properties={})
        result = rename_animal_df(df, "A1", animal)

        assert result.loc[1, "Animal"] == "A2"
        assert result.loc[2, "Animal"] == "A3"


class TestReassignDfTimedelta:
    """Tests for reassign_df_timedelta function."""

    def test_reassigns_timedelta_none_mode(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "DateTime": [base, base + pd.Timedelta("1h"), base + pd.Timedelta("2h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta(0), pd.Timedelta(0)],  # wrong initial values
        })

        result = reassign_df_timedelta(df, None)

        assert result["Timedelta"].iloc[0] == pd.Timedelta(0)
        assert result["Timedelta"].iloc[1] == pd.Timedelta("1h")
        assert result["Timedelta"].iloc[2] == pd.Timedelta("2h")

    def test_overlap_mode_per_run_timedelta(self):
        base1 = pd.Timestamp("2024-01-01")
        base2 = pd.Timestamp("2024-01-02")
        df = pd.DataFrame({
            "DateTime": [base1, base1 + pd.Timedelta("1h"), base2, base2 + pd.Timedelta("1h")],
            "Timedelta": [pd.Timedelta(0)] * 4,
            "Run": [1, 1, 2, 2],
        })

        result = reassign_df_timedelta(df, "overlap")

        # Each run starts from 0
        assert result["Timedelta"].iloc[0] == pd.Timedelta(0)
        assert result["Timedelta"].iloc[2] == pd.Timedelta(0)

    def test_does_not_touch_bin_column(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "DateTime": [base, base + pd.Timedelta("1h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta("1h")],
            "Bin": [99, 99],
        })

        result = reassign_df_timedelta(df, None)
        # Bin should remain unchanged — it's now materialized by the factor system.
        assert result["Bin"].iloc[0] == 99
        assert result["Bin"].iloc[1] == 99


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
