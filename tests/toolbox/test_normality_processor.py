"""Tests for tse_analytics.toolbox.normality.processor module."""

import matplotlib
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.toolbox.normality.processor import NormalityTestResult, get_normality_result

matplotlib.use("Agg")


class TestNormality:
    """Tests for test_normality processor function."""

    def test_total_mode_returns_result(self, analysis_df):
        result = get_normality_result(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.TOTAL),
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert len(result.report) > 0
        assert "<img" in result.report

    def test_animal_mode(self, analysis_df):
        result = get_normality_result(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report

    def test_factor_mode(self, analysis_df):
        result = get_normality_result(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.FACTOR, factor_name="Group"),
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report

    def test_run_mode(self, analysis_df):
        result = get_normality_result(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.RUN),
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report
