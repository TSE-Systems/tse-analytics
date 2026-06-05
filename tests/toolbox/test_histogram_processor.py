"""Tests for tse_analytics.toolbox.histogram.processor module."""

import matplotlib
from tse_analytics.toolbox.histogram.processor import HistogramResult, get_histogram_result

matplotlib.use("Agg")


class TestHistogram:
    """Tests for get_histogram_result processor function."""

    def test_factor_mode(self, analysis_dataset):
        result = get_histogram_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            factor_name="Group",
            figsize=(8, 6),
        )
        assert isinstance(result, HistogramResult)
