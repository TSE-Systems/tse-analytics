"""Tests for tse_analytics.toolbox.distribution.processor module."""

import matplotlib

matplotlib.use("Agg")

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.toolbox.distribution.processor import DistributionResult, get_distribution_result


class TestDistribution:
    """Tests for get_distribution_result processor function."""

    def test_box_plot_total_mode(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)
        assert "<img" in result.report

    def test_violin_plot_total_mode(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.TOTAL,
            factor_name=None,
            plot_type="Violin plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)
        assert "<img" in result.report

    def test_factor_mode(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.FACTOR,
            factor_name="Group",
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)

    def test_animal_mode(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.ANIMAL,
            factor_name=None,
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)

    def test_with_strip_points(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.FACTOR,
            factor_name="Group",
            plot_type="Box plot",
            show_points=True,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)
        assert "<img" in result.report

    def test_run_mode(self, analysis_dataset, analysis_df):
        result = get_distribution_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable_name="Metabolism",
            split_mode=SplitMode.RUN,
            factor_name=None,
            plot_type="Box plot",
            show_points=False,
            figsize=(8, 6),
        )
        assert isinstance(result, DistributionResult)
