"""Tests for tse_analytics.toolbox.regression.processor module."""

from tse_analytics.core.data.shared import ByAnimalConfig, Factor, FactorLevel, FactorRole
from tse_analytics.toolbox.regression.processor import RegressionResult, get_regression_result


class TestRegression:
    """Tests for get_regression_result processor function."""

    def test_returns_regression_result(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_regression_result(
            datatable=analysis_dataset.datatables["Main"],
            covariate=variables["Activity"],
            response=variables["Metabolism"],
            factor_name="Group",
        )
        assert isinstance(result, RegressionResult)

    def test_report_is_html_with_per_level_table(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_regression_result(
            datatable=analysis_dataset.datatables["Main"],
            covariate=variables["Activity"],
            response=variables["Metabolism"],
            factor_name="Group",
        )
        assert "<table" in result.report
        assert "Level:" in result.report

    def test_swapped_variables(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_regression_result(
            datatable=analysis_dataset.datatables["Main"],
            covariate=variables["Metabolism"],
            response=variables["Activity"],
            factor_name="Group",
        )
        assert isinstance(result, RegressionResult)

    def test_same_covariate_and_response_is_handled(self, analysis_dataset, analysis_df):
        variables = analysis_dataset.datatables["Main"].variables

        result = get_regression_result(
            datatable=analysis_dataset.datatables["Main"],
            covariate=variables["Activity"],
            response=variables["Activity"],
            factor_name="Group",
        )
        assert isinstance(result, RegressionResult)
        assert "same variable" in result.report

    def test_level_with_insufficient_data_adds_note(self, analysis_dataset, analysis_df):
        """A factor level with a single animal yields <2 aggregated points -> a note, not a crash."""
        datatable = analysis_dataset.datatables["Main"]
        variables = datatable.variables

        # "Solo" level has a single animal; the rest fall into "Rest".
        analysis_dataset.factors["Solo"] = Factor(
            name="Solo",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Solo": FactorLevel(name="Solo", color="#FF0000", animal_ids=["M1"]),
                "Rest": FactorLevel(name="Rest", color="#00FF00", animal_ids=["M2", "M3", "M4", "M5", "M6"]),
            },
        )
        datatable.df["Solo"] = datatable.df["Animal"].map(lambda a: "Solo" if a == "M1" else "Rest").astype("category")

        result = get_regression_result(
            datatable=datatable,
            covariate=variables["Activity"],
            response=variables["Metabolism"],
            factor_name="Solo",
        )
        assert isinstance(result, RegressionResult)
        assert "not enough data" in result.report
