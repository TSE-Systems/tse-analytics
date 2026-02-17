"""Tests for tse_analytics.toolbox.ancova.processor module."""

import pytest
from tse_analytics.toolbox.ancova.processor import AncovaResult, get_ancova_result


class TestAncova:
    """Tests for get_ancova_result processor function."""

    def test_returns_ancova_result(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize="hedges",
            padjust="none",
        )
        assert isinstance(result, AncovaResult)

    def test_report_contains_ancova_table(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize="hedges",
            padjust="none",
        )
        assert "ANCOVA" in result.report

    def test_report_contains_pairwise_tests(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize="hedges",
            padjust="none",
        )
        assert "pairwise" in result.report.lower()

    def test_report_is_html(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize="hedges",
            padjust="none",
        )
        assert "<table" in result.report

    @pytest.mark.parametrize("effsize", ["none", "cohen", "eta-square", "hedges", "r"])
    def test_different_effsize(self, analysis_dataset, analysis_df, effsize):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize=effsize,
            padjust="none",
        )
        assert isinstance(result, AncovaResult)

    @pytest.mark.parametrize("padjust", ["none", "bonf", "holm"])
    def test_different_padjust(self, analysis_dataset, analysis_df, padjust):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Metabolism"],
            covariate_variable=variables["Activity"],
            factor_name="Group",
            effsize="hedges",
            padjust=padjust,
        )
        assert isinstance(result, AncovaResult)

    def test_swapped_variables(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_ancova_result(
            dataset=analysis_dataset,
            df=analysis_df.copy(),
            dependent_variable=variables["Activity"],
            covariate_variable=variables["Metabolism"],
            factor_name="Group",
            effsize="hedges",
            padjust="none",
        )
        assert isinstance(result, AncovaResult)
