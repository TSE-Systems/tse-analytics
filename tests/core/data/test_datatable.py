"""Tests for tse_analytics.core.data.datatable module."""

from datetime import timedelta

import pandas as pd
import pytest
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    ByTimeIntervalConfig,
    Factor,
    FactorRole,
    Variable,
)


class TestDatatableInit:
    """Tests for Datatable initialization."""

    def test_assigns_uuid(self, sample_datatable):
        assert sample_datatable.id is not None

    def test_stores_name(self, sample_datatable):
        assert sample_datatable.name == "Main"

    def test_stores_description(self, sample_datatable):
        assert sample_datatable.description == "Main datatable"

    def test_stores_sampling_interval(self, sample_datatable):
        assert sample_datatable.sample_interval == pd.Timedelta("1h")


class TestDatatableProperties:
    """Tests for Datatable properties."""

    def test_start_timestamp(self, sample_datatable):
        result = sample_datatable.start_timestamp
        assert isinstance(result, pd.Timestamp)
        assert result == pd.Timestamp("2024-01-01 00:00:00")

    def test_end_timestamp(self, sample_datatable):
        result = sample_datatable.end_timestamp
        assert isinstance(result, pd.Timestamp)
        assert result == pd.Timestamp("2024-01-01 04:00:00")

    def test_duration(self, sample_datatable):
        duration = sample_datatable.duration
        assert duration == pd.Timedelta("4h")


class TestGetDefaultColumns:
    """Tests for Datatable.get_default_columns."""

    def test_includes_base_columns(self, sample_datatable):
        columns = sample_datatable.get_default_columns()
        assert "Animal" in columns
        assert "Timedelta" in columns
        assert "DateTime" in columns

    def test_no_experiment_column_when_absent(self, sample_datatable):
        columns = sample_datatable.get_default_columns()
        assert "Experiment" not in columns


class TestGetCategoricalColumns:
    """Tests for Datatable.get_categorical_columns."""

    def test_returns_category_columns(self, sample_datatable):
        columns = sample_datatable.get_categorical_columns()
        assert "Animal" in columns


class TestRenameAnimal:
    """Tests for Datatable.rename_animal."""

    def test_rename_animal(self, sample_datatable):
        new_animal = Animal(id="NewA1", properties={})
        sample_datatable.rename_animal("A1", new_animal)

        assert "NewA1" in sample_datatable.df["Animal"].values
        assert "A1" not in sample_datatable.df["Animal"].values


class TestExcludeAnimals:
    """Tests for Datatable.exclude_animals."""

    def test_filters_rows(self, sample_datatable):
        original_len = len(sample_datatable.df)
        sample_datatable.exclude_animals({"A3"})

        assert len(sample_datatable.df) < original_len
        assert "A3" not in sample_datatable.df["Animal"].values

    def test_removes_unused_categories(self, sample_datatable):
        sample_datatable.exclude_animals({"A3"})
        categories = sample_datatable.df["Animal"].cat.categories.tolist()
        assert "A3" not in categories


class TestExcludeTime:
    """Tests for Datatable.exclude_time."""

    def test_filters_datetime_range(self, sample_datatable):
        original_len = len(sample_datatable.df)

        # Exclude the first 2 hours
        sample_datatable.exclude_time(
            pd.Timestamp("2024-01-01 00:00:00"),
            pd.Timestamp("2024-01-01 01:30:00"),
        )

        assert len(sample_datatable.df) < original_len


class TestTrimTime:
    """Tests for Datatable.trim_time."""

    def test_keeps_only_range(self, sample_datatable):
        sample_datatable.trim_time(
            pd.Timestamp("2024-01-01 01:00:00"),
            pd.Timestamp("2024-01-01 03:00:00"),
        )

        min_dt = sample_datatable.df["DateTime"].min()
        max_dt = sample_datatable.df["DateTime"].max()

        assert min_dt >= pd.Timestamp("2024-01-01 01:00:00")
        assert max_dt <= pd.Timestamp("2024-01-01 03:00:00")


class TestSetFactors:
    """Tests for Datatable.set_factors."""

    def test_adds_factor_column(self, sample_datatable, sample_factor):
        sample_datatable.set_factors({"Group": sample_factor})
        assert "Group" in sample_datatable.df.columns

    def test_factor_column_is_categorical(self, sample_datatable, sample_factor):
        sample_datatable.set_factors({"Group": sample_factor})
        assert sample_datatable.df["Group"].dtype.name == "category"

    def test_assigns_correct_levels(self, sample_datatable, sample_factor):
        sample_datatable.set_factors({"Group": sample_factor})
        df = sample_datatable.df

        # A1 should be Control
        a1_groups = df[df["Animal"] == "A1"]["Group"].unique()
        assert "Control" in a1_groups

        # A2 should be Treatment
        a2_groups = df[df["Animal"] == "A2"]["Group"].unique()
        assert "Treatment" in a2_groups


class TestGetFilteredDf:
    """Tests for Datatable.get_filtered_df."""

    def test_returns_specified_columns(self, sample_datatable):
        df = sample_datatable.get_filtered_df(["Animal", "Weight"])
        assert set(df.columns) == {"Animal", "Weight"}


class TestDeleteVariables:
    """Tests for Datatable.delete_variables."""

    def test_removes_from_variables_dict(self, sample_datatable):
        sample_datatable.delete_variables(["Weight"])
        assert "Weight" not in sample_datatable.variables

    def test_drops_delete_variables(self, sample_datatable):
        sample_datatable.delete_variables(["Weight"])
        assert "Weight" not in sample_datatable.df.columns

    def test_nonexistent_variable_is_ignored(self, sample_datatable):
        # Should not raise
        sample_datatable.delete_variables(["NonExistent"])


class TestRenameVariables:
    """Tests for Datatable.rename_variables."""

    def test_renames_in_variables_dict(self, sample_datatable):
        sample_datatable.rename_variables({"Weight": "Mass"})
        assert "Mass" in sample_datatable.variables
        assert "Weight" not in sample_datatable.variables

    def test_renames_in_dataframes(self, sample_datatable):
        sample_datatable.rename_variables({"Weight": "Mass"})
        assert "Mass" in sample_datatable.df.columns

    def test_updates_variable_name_field(self, sample_datatable):
        sample_datatable.rename_variables({"Weight": "Mass"})
        assert sample_datatable.variables["Mass"].name == "Mass"


class TestDatatableClone:
    """Tests for Datatable.clone."""

    def test_returns_new_instance(self, sample_datatable):
        clone = sample_datatable.clone()
        assert clone is not sample_datatable

    def test_has_independent_df(self, sample_datatable):
        clone = sample_datatable.clone()
        clone.df.iloc[0, clone.df.columns.get_loc("Weight")] = 999.0
        assert sample_datatable.df.iloc[0, sample_datatable.df.columns.get_loc("Weight")] != 999.0

    def test_assigns_fresh_id(self, sample_datatable):
        clone = sample_datatable.clone()
        assert clone.id != sample_datatable.id

    def test_preserves_outliers_settings(self, sample_datatable):
        from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings

        sample_datatable.outliers_settings = OutliersSettings(mode=OutliersMode.REMOVE)
        clone = sample_datatable.clone()
        assert clone.outliers_settings.mode == OutliersMode.REMOVE

    def test_outliers_settings_are_independent(self, sample_datatable):
        from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings

        sample_datatable.outliers_settings = OutliersSettings(mode=OutliersMode.REMOVE)
        clone = sample_datatable.clone()
        clone.outliers_settings.mode = OutliersMode.OFF
        assert sample_datatable.outliers_settings.mode == OutliersMode.REMOVE


class TestApplyByTimeInterval:
    """Tests for the BY_TIME_INTERVAL factor applier."""

    def test_creates_ordered_categorical_column(self, sample_datatable):
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={},
        )
        sample_datatable.set_factors({"Hour": factor})
        column = sample_datatable.df["Hour"]
        assert column.dtype.name == "category"
        assert column.cat.ordered

    def test_hour_indices_match_one_hour_interval(self, sample_datatable):
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={},
        )
        sample_datatable.set_factors({"Hour": factor})
        # sample_df spans 5 hourly timepoints (indices 0..4)
        column = sample_datatable.df["Hour"]
        assert set(column.unique().tolist()) == {"Hour 0", "Hour 1", "Hour 2", "Hour 3", "Hour 4"}
        assert list(column.cat.categories) == ["Hour 0", "Hour 1", "Hour 2", "Hour 3", "Hour 4"]

    def test_auto_populates_levels_when_empty(self, sample_datatable):
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={},
        )
        sample_datatable.set_factors({"Hour": factor})
        assert list(factor.levels.keys()) == ["Hour 0", "Hour 1", "Hour 2", "Hour 3", "Hour 4"]

    def test_redefining_to_24h_collapses_to_zero(self, sample_datatable):
        factor = Factor(
            name="Days",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(days=1)),
            levels={},
        )
        sample_datatable.set_factors({"Days": factor})
        # All 5 timepoints span < 24h, so they all fall in bin 0.
        assert (sample_datatable.df["Days"] == "Day 0").all()

    def test_custom_factor_name_creates_named_column(self, sample_datatable):
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={},
        )
        sample_datatable.set_factors({"Hour": factor})
        assert "Hour" in sample_datatable.df.columns
        assert sample_datatable.df["Hour"].dtype.name == "category"


class TestFromDataframe:
    """Tests for the Datatable.from_dataframe universal builder."""

    @pytest.fixture
    def result_df(self):
        """A cross-sectional result frame: one row per animal, no DateTime/Timedelta.

        MESOR is deliberately non-integer so convert_dtypes() keeps it Float64 (whole-number
        floats would be downcast to Int64), while N exercises the nullable-int path.
        """
        return pd.DataFrame({
            "Animal": ["A1", "A2", "A3"],
            "MESOR": [1.5, 2.5, 3.5],
            "Amplitude": [0.5, 0.6, 0.7],
            "N": [10, 20, 30],
        })

    def test_auto_generates_variables_for_numeric_non_id_columns(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert set(dt.variables.keys()) == {"MESOR", "Amplitude", "N"}
        assert "Animal" not in dt.variables

    def test_casts_id_column_to_category(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert dt.df["Animal"].dtype.name == "category"

    def test_records_origin_metadata(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import META_ORIGIN, Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert dt.metadata[META_ORIGIN] == "Chronobiology"

    def test_normalizes_to_nullable_dtypes(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert dt.df["MESOR"].dtype.name == "Float64"
        assert dt.df["N"].dtype.name == "Int64"

    def test_default_description(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert dt.description == "Chronobiology result: Chrono"

    def test_does_not_mutate_source_df(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        # The caller's frame is untouched — the id column was not cast to category in place.
        assert result_df["Animal"].dtype.name != "category"

    def test_explicit_variables_used_verbatim(self, sample_dataset):
        """A helper column (e.g. Bin) must NOT become a variable when variables= is given."""
        from tse_analytics.core.data.datatable import Datatable

        df = pd.DataFrame({
            "Animal": ["A1", "A2"],
            "Bin": pd.array([0, 1], dtype="UInt64"),
            "Feed": pd.array([1.0, 2.0], dtype="Float64"),
        })
        variables = {"Feed": Variable("Feed", "g", "Feed", "Float64", Aggregation.SUM, False)}
        dt = Datatable.from_dataframe(sample_dataset, "DF", df, origin="X", variables=variables, apply_factors=False)
        assert set(dt.variables.keys()) == {"Feed"}
        assert "Bin" not in dt.variables

    def test_normalize_dtypes_false_preserves_dtypes(self, sample_dataset):
        from tse_analytics.core.data.datatable import Datatable

        df = pd.DataFrame({"Animal": ["A1"], "Bin": pd.array([0], dtype="UInt64")})
        dt = Datatable.from_dataframe(
            sample_dataset, "DF", df, origin="X", variables={}, apply_factors=False, normalize_dtypes=False
        )
        assert dt.df["Bin"].dtype.name == "UInt64"

    def test_sample_interval_marks_regular_timeseries(self, sample_dataset):
        from tse_analytics.core.data.datatable import Datatable

        base = pd.Timestamp("2024-01-01")
        df = pd.DataFrame({
            "Animal": ["A1", "A1"],
            "DateTime": [base, base + pd.Timedelta("1h")],
            "Timedelta": [pd.Timedelta(0), pd.Timedelta("1h")],
            "Value": [1.0, 2.0],
        })
        dt = Datatable.from_dataframe(
            sample_dataset, "TS", df, origin="X", sample_interval=pd.Timedelta("1h"), apply_factors=False
        )
        assert dt.is_regular_timeseries is True
        assert isinstance(dt.sample_interval, pd.Timedelta)
        assert dt.sample_interval == pd.Timedelta("1h")

    def test_cross_sectional_is_not_regular_timeseries(self, sample_dataset, result_df):
        from tse_analytics.core.data.datatable import Datatable

        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology")
        assert dt.is_regular_timeseries is False

    def test_apply_factors_materializes_group_when_animal_present(self, sample_dataset, sample_factor, result_df):
        from tse_analytics.core.data.datatable import Datatable

        sample_dataset.factors["Group"] = sample_factor
        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology", apply_factors=True)
        assert "Group" in dt.df.columns

    def test_apply_factors_false_skips_factor_columns(self, sample_dataset, sample_factor, result_df):
        from tse_analytics.core.data.datatable import Datatable

        sample_dataset.factors["Group"] = sample_factor
        dt = Datatable.from_dataframe(sample_dataset, "Chrono", result_df, origin="Chronobiology", apply_factors=False)
        assert "Group" not in dt.df.columns


class TestTimeseriesGuards:
    """Tests for is_timeseries and the time-column guards on cross-sectional datatables."""

    @pytest.fixture
    def cross_sectional_datatable(self, sample_dataset):
        from tse_analytics.core.data.datatable import Datatable

        df = pd.DataFrame({"Animal": ["A1", "A2"], "MESOR": [1.0, 2.0]})
        return Datatable.from_dataframe(sample_dataset, "Cross", df, origin="X", apply_factors=False)

    def test_is_timeseries_true_for_timeseries(self, sample_datatable):
        assert sample_datatable.is_timeseries is True

    def test_is_timeseries_false_for_cross_sectional(self, cross_sectional_datatable):
        assert cross_sectional_datatable.is_timeseries is False

    def test_start_timestamp_raises_off_timeseries(self, cross_sectional_datatable):
        with pytest.raises(ValueError):
            _ = cross_sectional_datatable.start_timestamp

    def test_end_timestamp_raises_off_timeseries(self, cross_sectional_datatable):
        with pytest.raises(ValueError):
            _ = cross_sectional_datatable.end_timestamp

    def test_duration_raises_off_timeseries(self, cross_sectional_datatable):
        with pytest.raises(ValueError):
            _ = cross_sectional_datatable.duration

    def test_exclude_time_is_noop_off_timeseries(self, cross_sectional_datatable):
        before = cross_sectional_datatable.df.copy()
        cross_sectional_datatable.exclude_time(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))
        pd.testing.assert_frame_equal(cross_sectional_datatable.df, before)

    def test_trim_time_is_noop_off_timeseries(self, cross_sectional_datatable):
        before = cross_sectional_datatable.df.copy()
        cross_sectional_datatable.trim_time(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02"))
        pd.testing.assert_frame_equal(cross_sectional_datatable.df, before)

    def test_resample_is_noop_off_timeseries(self, cross_sectional_datatable):
        before = cross_sectional_datatable.df.copy()
        cross_sectional_datatable.resample(pd.Timedelta("1h"))
        pd.testing.assert_frame_equal(cross_sectional_datatable.df, before)
