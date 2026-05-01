"""Tests for tse_analytics.toolbox.correlation.processor module."""

import matplotlib
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.toolbox.correlation.processor import CorrelationResult, get_correlation_result

matplotlib.use("Agg")


class TestCorrelation:
    """Tests for get_correlation_result processor function."""

    def test_report_contains_ttest(self, analysis_dataset):
        result = get_correlation_result(
            datatable=analysis_dataset.datatables["Main"],
            x_var_name="Metabolism",
            y_var_name="Activity",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            figsize=(8, 6),
        )
        assert "t-test" in result.report.lower()

    def test_report_contains_correlation(self, analysis_dataset):
        result = get_correlation_result(
            datatable=analysis_dataset.datatables["Main"],
            x_var_name="Metabolism",
            y_var_name="Activity",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            figsize=(8, 6),
        )
        assert "pearson" in result.report.lower()

    def test_animal_mode(self, analysis_dataset):
        result = get_correlation_result(
            datatable=analysis_dataset.datatables["Main"],
            x_var_name="Metabolism",
            y_var_name="Activity",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            figsize=(8, 6),
        )
        assert isinstance(result, CorrelationResult)

    def test_factor_mode(self, analysis_dataset):
        result = get_correlation_result(
            datatable=analysis_dataset.datatables["Main"],
            x_var_name="Metabolism",
            y_var_name="Activity",
            grouping_settings=GroupingSettings(mode=GroupingMode.FACTOR, factor_name="Group"),
            figsize=(8, 6),
        )
        assert isinstance(result, CorrelationResult)
