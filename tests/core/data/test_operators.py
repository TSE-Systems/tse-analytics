"""Tests for core/data/operators/ pipe operator functions."""

import pandas as pd
from tse_analytics.core.data.operators.outliers_pipe_operator import process_outliers
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
