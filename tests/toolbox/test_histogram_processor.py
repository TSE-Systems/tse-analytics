"""Tests for tse_analytics.toolbox.histogram.processor module."""

import matplotlib

matplotlib.use("Agg")

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.toolbox.histogram.processor import HistogramResult, get_histogram_result


class TestHistogram:
    """Tests for get_histogram_result processor function."""

    def test_total_mode(self, analysis_dataset, analysis_df):
        result = get_histogram_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
        assert "<img" in result.report

    def test_animal_mode(self, analysis_dataset, analysis_df):
        result = get_histogram_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.ANIMAL,
            factor_name=None,
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
        assert "<img" in result.report

    def test_factor_mode(self, analysis_dataset, analysis_df):
        result = get_histogram_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.FACTOR,
            factor_name="Group",
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)

    def test_run_mode(self, analysis_dataset, analysis_df):
        result = get_histogram_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.RUN,
            factor_name=None,
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
