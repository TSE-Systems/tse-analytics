"""Tests for tse_analytics.toolbox.correlation.processor module."""

import matplotlib

matplotlib.use("Agg")

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.toolbox.correlation.processor import CorrelationResult, get_correlation_result


class TestCorrelation:
    """Tests for get_correlation_result processor function."""

    def test_total_mode(self, analysis_dataset, analysis_df):
        result = get_correlation_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            x_var_name="Metabolism",
            y_var_name="Activity",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert isinstance(result, CorrelationResult)
        assert "<img" in result.report

    def test_report_contains_ttest(self, analysis_dataset, analysis_df):
        result = get_correlation_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            x_var_name="Metabolism",
            y_var_name="Activity",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert "t-test" in result.report.lower()

    def test_report_contains_correlation(self, analysis_dataset, analysis_df):
        result = get_correlation_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            x_var_name="Metabolism",
            y_var_name="Activity",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert "pearson" in result.report.lower()

    def test_animal_mode(self, analysis_dataset, analysis_df):
        result = get_correlation_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            x_var_name="Metabolism",
            y_var_name="Activity",
            split_mode=SplitMode.ANIMAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert isinstance(result, CorrelationResult)

    def test_factor_mode(self, analysis_dataset, analysis_df):
        result = get_correlation_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            x_var_name="Metabolism",
            y_var_name="Activity",
            split_mode=SplitMode.FACTOR,
            factor_name="Group",
            figsize=(8, 6),
        )
        assert isinstance(result, CorrelationResult)
