"""Tests for tse_analytics.toolbox.one_way_anova.processor module."""

import matplotlib

matplotlib.use("Agg")

from tse_analytics.toolbox.one_way_anova.processor import OneWayAnovaResult, get_one_way_anova_result


class TestOneWayAnova:
    """Tests for get_one_way_anova_result processor function."""

    def test_returns_result(self, analysis_dataset, analysis_df):
        variable = analysis_dataset.datatables["Main"].variables["Metabolism"]

        result = get_one_way_anova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable=variable,
            factor_name="Group",
            effsize="hedges",
            figsize=(8, 6),
        )
        assert isinstance(result, OneWayAnovaResult)

    def test_report_contains_anova_table(self, analysis_dataset, analysis_df):
        variable = analysis_dataset.datatables["Main"].variables["Metabolism"]

        result = get_one_way_anova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable=variable,
            factor_name="Group",
            effsize="hedges",
            figsize=(8, 6),
        )
        assert "Factor: Group" in result.report

    def test_report_contains_normality(self, analysis_dataset, analysis_df):
        variable = analysis_dataset.datatables["Main"].variables["Metabolism"]

        result = get_one_way_anova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable=variable,
            factor_name="Group",
            effsize="hedges",
            figsize=(8, 6),
        )
        assert "normality" in result.report.lower()

    def test_report_contains_post_hoc(self, analysis_dataset, analysis_df):
        variable = analysis_dataset.datatables["Main"].variables["Metabolism"]

        result = get_one_way_anova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable=variable,
            factor_name="Group",
            effsize="hedges",
            figsize=(8, 6),
        )
        # Should contain either Tukey or Games-Howell
        assert "post-hoc" in result.report.lower()

    def test_report_contains_image(self, analysis_dataset, analysis_df):
        variable = analysis_dataset.datatables["Main"].variables["Metabolism"]

        result = get_one_way_anova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            variable=variable,
            factor_name="Group",
            effsize="hedges",
            figsize=(8, 6),
        )
        assert "<img" in result.report
