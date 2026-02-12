"""Tests for tse_analytics.toolbox.normality.processor module."""

import matplotlib

matplotlib.use("Agg")


from tse_analytics.core.data.shared import SplitMode
from tse_analytics.toolbox.normality.processor import NormalityTestResult
from tse_analytics.toolbox.normality.processor import test_normality as _test_normality


class TestNormality:
    """Tests for test_normality processor function."""

    def test_total_mode_returns_result(self, analysis_df):
        result = _test_normality(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert len(result.report) > 0
        assert "<img" in result.report

    def test_animal_mode(self, analysis_df):
        result = _test_normality(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.ANIMAL,
            factor_name=None,
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report

    def test_factor_mode(self, analysis_df):
        result = _test_normality(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.FACTOR,
            factor_name="Group",
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report

    def test_run_mode(self, analysis_df):
        result = _test_normality(
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.RUN,
            factor_name=None,
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report
