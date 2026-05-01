"""Tests for tse_analytics.toolbox.normality.processor module."""

import matplotlib
from tse_analytics.toolbox.normality.processor import NormalityTestResult, get_normality_result

matplotlib.use("Agg")


class TestNormality:
    """Tests for test_normality processor function."""

    def test_factor_mode(self, analysis_dataset):
        result = get_normality_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            factor_name="Group",
            figsize=(6, 4),
        )
        assert isinstance(result, NormalityTestResult)
        assert "<img" in result.report
