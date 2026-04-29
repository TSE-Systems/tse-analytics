"""Tests for tse_analytics.toolbox.histogram.processor module."""

import matplotlib
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.toolbox.histogram.processor import HistogramResult, get_histogram_result

matplotlib.use("Agg")


class TestHistogram:
    """Tests for get_histogram_result processor function."""

    def test_total_mode(self, analysis_dataset):
        result = get_histogram_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.TOTAL),
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
        assert "<img" in result.report

    def test_animal_mode(self, analysis_dataset):
        result = get_histogram_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
        assert "<img" in result.report

    def test_factor_mode(self, analysis_dataset):
        result = get_histogram_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.FACTOR, factor_name="Group"),
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)

    def test_run_mode(self, analysis_dataset):
        result = get_histogram_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.RUN),
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
