"""Tests for tse_analytics.core.data.datatable module."""

import pandas as pd
from tse_analytics.core.data.shared import Animal


class TestDatatableInit:
    """Tests for Datatable initialization."""

    def test_assigns_uuid(self, sample_datatable):
        assert sample_datatable.id is not None

    def test_stores_name(self, sample_datatable):
        assert sample_datatable.name == "Main"

    def test_stores_description(self, sample_datatable):
        assert sample_datatable.description == "Main datatable"

    def test_stores_sampling_interval(self, sample_datatable):
        assert sample_datatable.sampling_interval == pd.Timedelta("1h")


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

    def test_includes_bin_when_present(self, sample_datatable):
        columns = sample_datatable.get_default_columns()
        assert "Bin" in columns

    def test_includes_base_columns(self, sample_datatable):
        columns = sample_datatable.get_default_columns()
        assert "Animal" in columns
        assert "Timedelta" in columns
        assert "DateTime" in columns

    def test_no_run_column_when_absent(self, sample_datatable):
        columns = sample_datatable.get_default_columns()
        assert "Run" not in columns


class TestGetCategoricalColumns:
    """Tests for Datatable.get_categorical_columns."""

    def test_returns_category_columns(self, sample_datatable):
        columns = sample_datatable.get_categorical_columns()
        assert "Animal" in columns


class TestRenameAnimal:
    """Tests for Datatable.rename_animal."""

    def test_rename_animal(self, sample_datatable):
        new_animal = Animal(enabled=True, id="NewA1", color="#FF0000", properties={})
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

    def test_filters_by_enabled_animals(self, sample_datatable):
        # A3 is disabled in sample_animals
        df = sample_datatable.get_filtered_df(["Animal", "Weight"])

        assert "A3" not in df["Animal"].values
        assert "A1" in df["Animal"].values

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
