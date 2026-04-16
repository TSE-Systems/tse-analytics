"""Tests for core/data/operators/ pipe operator functions."""

import pandas as pd
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.operators.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import Aggregation, Variable


class TestProcessOutliers:
    """Tests for process_outliers operator."""

    def test_no_op_when_no_flagged_variables(self, sample_df):
        variables = {
            "Weight": Variable("Weight", "g", "weight", "Float64", Aggregation.MEAN, remove_outliers=False),
        }
        settings = OutliersSettings(mode=OutliersMode.REMOVE, iqr_multiplier=1.5)

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
            "Value": Variable("Value", "u", "val", "Float64", Aggregation.MEAN, remove_outliers=True),
        }
        settings = OutliersSettings(mode=OutliersMode.REMOVE, iqr_multiplier=1.5)

        result = process_outliers(df, settings, variables)
        assert 100 not in result["Value"].values

    def test_respects_coefficient(self):
        # With very large coefficient, nothing should be removed
        df = pd.DataFrame({
            "Animal": ["A1"] * 10,
            "Value": [10, 11, 10, 12, 11, 10, 11, 12, 10, 100],
        })
        df["Animal"] = df["Animal"].astype("category")

        variables = {
            "Value": Variable("Value", "u", "val", "Float64", Aggregation.MEAN, remove_outliers=True),
        }
        settings = OutliersSettings(mode=OutliersMode.REMOVE, iqr_multiplier=100.0)  # Very large coefficient

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
