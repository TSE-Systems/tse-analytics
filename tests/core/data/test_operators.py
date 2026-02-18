"""Tests for core/data/operators/ pipe operator functions."""

import pandas as pd
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.operators.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.operators.group_by_pipe_operator import group_by_columns
from tse_analytics.core.data.operators.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import Aggregation, SplitMode, Variable


class TestFilterAnimals:
    """Tests for filter_animals operator."""

    def test_returns_all_when_all_enabled(self, sample_df, sample_animals):
        # Make all enabled
        for a in sample_animals.values():
            a.enabled = True

        result = filter_animals(sample_df, sample_animals)
        assert len(result) == len(sample_df)

    def test_filters_disabled_animals(self, sample_df, sample_animals):
        # A3 is already disabled
        result = filter_animals(sample_df, sample_animals)

        assert "A3" not in result["Animal"].values
        assert "A1" in result["Animal"].values
        assert "A2" in result["Animal"].values

    def test_removes_unused_categories(self, sample_df, sample_animals):
        result = filter_animals(sample_df, sample_animals)
        categories = result["Animal"].cat.categories.tolist()
        assert "A3" not in categories

    def test_resets_index(self, sample_df, sample_animals):
        result = filter_animals(sample_df, sample_animals)
        assert result.index[0] == 0
        assert result.index[-1] == len(result) - 1


class TestProcessOutliers:
    """Tests for process_outliers operator."""

    def test_no_op_when_no_flagged_variables(self, sample_df):
        variables = {
            "Weight": Variable("Weight", "g", "weight", "float", Aggregation.MEAN, remove_outliers=False),
        }
        settings = OutliersSettings(OutliersMode.REMOVE, 1.5)

        result = process_outliers(sample_df, settings, variables)
        assert len(result) == len(sample_df)

    def test_removes_outlier_rows(self):
        # Create data with a clear outlier
        df = pd.DataFrame({
            "Animal": ["A1"] * 10,
            "Value": [10, 11, 10, 12, 11, 10, 11, 12, 10, 100],  # 100 is an outlier
        })
        df["Animal"] = df["Animal"].astype("category")

        variables = {
            "Value": Variable("Value", "u", "val", "float", Aggregation.MEAN, remove_outliers=True),
        }
        settings = OutliersSettings(OutliersMode.REMOVE, 1.5)

        result = process_outliers(df, settings, variables)
        assert 100 not in result["Value"].values
        assert len(result) < len(df)

    def test_respects_coefficient(self):
        # With very large coefficient, nothing should be removed
        df = pd.DataFrame({
            "Animal": ["A1"] * 10,
            "Value": [10, 11, 10, 12, 11, 10, 11, 12, 10, 100],
        })
        df["Animal"] = df["Animal"].astype("category")

        variables = {
            "Value": Variable("Value", "u", "val", "float", Aggregation.MEAN, remove_outliers=True),
        }
        settings = OutliersSettings(OutliersMode.REMOVE, 100.0)  # Very large coefficient

        result = process_outliers(df, settings, variables)
        assert len(result) == len(df)


class TestProcessTimeIntervalBinning:
    """Tests for process_time_interval_binning operator."""

    def test_returns_empty_for_empty_df(self):
        df = pd.DataFrame()
        settings = TimeIntervalsBinningSettings("hour", 1)
        result = process_time_interval_binning(df, settings, {})
        assert result.empty

    def test_aggregates_by_hourly_intervals(self):
        base = pd.Timestamp("2024-01-01")
        # 2 animals, 4 half-hour intervals → should aggregate to 2 hourly bins
        rows = []
        for animal in ["A1", "A2"]:
            for i in range(4):
                rows.append({
                    "Animal": animal,
                    "DateTime": base + pd.Timedelta(minutes=30 * i),
                    "Timedelta": pd.Timedelta(minutes=30 * i),
                    "Weight": 25.0 + i,
                })
        df = pd.DataFrame(rows)
        df["Animal"] = df["Animal"].astype("category")
        df["Timedelta"] = pd.to_timedelta(df["Timedelta"])

        variables = {
            "Weight": Variable("Weight", "g", "weight", "float", Aggregation.MEAN, remove_outliers=False),
        }
        settings = TimeIntervalsBinningSettings("hour", 1)

        result = process_time_interval_binning(df, settings, variables, origin=base)
        assert "Bin" in result.columns
        # Should have 2 bins per animal → 4 rows total
        assert len(result) == 4

    def test_inserts_bin_column(self):
        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "Animal": pd.Categorical(["A1", "A1"]),
            "DateTime": [base, base + pd.Timedelta("1h")],
            "Timedelta": pd.to_timedelta([pd.Timedelta("0h"), pd.Timedelta("1h")]),
            "Val": [1.0, 2.0],
        })

        variables = {"Val": Variable("Val", "u", "v", "float", Aggregation.MEAN, remove_outliers=False)}
        settings = TimeIntervalsBinningSettings("hour", 1)

        result = process_time_interval_binning(df, settings, variables, origin=base)
        assert "Bin" in result.columns
        assert result["Bin"].iloc[0] == 0


class TestGroupByColumns:
    """Tests for group_by_columns operator."""

    def _make_binned_df(self):
        """Helper to create df with Bin column for grouping tests."""
        df = pd.DataFrame({
            "Animal": pd.Categorical(["A1", "A2", "A1", "A2"]),
            "Bin": [0, 0, 1, 1],
            "DateTime": pd.to_datetime(["2024-01-01"] * 4),
            "Timedelta": pd.to_timedelta(["0h", "0h", "1h", "1h"]),
            "Weight": [20.0, 30.0, 22.0, 32.0],
            "Group": pd.Categorical(["Ctrl", "Treat", "Ctrl", "Treat"]),
        })
        return df

    def test_animal_mode_returns_unchanged(self):
        df = self._make_binned_df()
        variables = {"Weight": Variable("Weight", "g", "w", "float", Aggregation.MEAN, remove_outliers=False)}

        result = group_by_columns(df, variables, SplitMode.ANIMAL, "Group")
        assert len(result) == len(df)

    def test_total_mode_aggregates_all_animals(self):
        df = self._make_binned_df()
        variables = {"Weight": Variable("Weight", "g", "w", "float", Aggregation.MEAN, remove_outliers=False)}

        result = group_by_columns(df, variables, SplitMode.TOTAL, "Group")
        # Should have 2 bins (one per bin)
        assert len(result) == 2
        # First bin should be mean of 20 and 30 = 25
        assert result.loc[result["Bin"] == 0, "Weight"].iloc[0] == 25.0

    def test_factor_mode_groups_by_factor(self):
        df = self._make_binned_df()
        variables = {"Weight": Variable("Weight", "g", "w", "float", Aggregation.MEAN, remove_outliers=False)}

        result = group_by_columns(df, variables, SplitMode.FACTOR, "Group")
        # 2 bins × 2 groups = 4 rows
        assert len(result) == 4
