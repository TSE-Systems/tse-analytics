"""Tests for tse_analytics.toolbox.distribution.processor module."""

import matplotlib

matplotlib.use("Agg")

from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.toolbox.distribution.processor import DistributionResult, get_distribution_result


class TestDistribution:
    """Tests for get_distribution_result processor function."""

    def test_factor_mode(self, analysis_dataset):
        result = get_distribution_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.FACTOR, factor_name="Group"),
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)

    def test_animal_mode(self, analysis_dataset):
        result = get_distribution_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.ANIMAL),
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)

    def test_with_strip_points(self, analysis_dataset):
        result = get_distribution_result(
            datatable=analysis_dataset.datatables["Main"],
            variable_name="Metabolism",
            grouping_settings=GroupingSettings(mode=GroupingMode.FACTOR, factor_name="Group"),
            plot_type="Box plot",
            show_points=True,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)
        assert "<img" in result.report
