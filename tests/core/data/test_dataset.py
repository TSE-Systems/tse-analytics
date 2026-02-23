"""Tests for tse_analytics.core.data.dataset module."""

import pickle
from unittest.mock import patch

import pandas as pd
from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import Animal


class TestDatasetInit:
    """Tests for Dataset initialization."""

    def test_generates_uuid(self, sample_dataset):
        assert sample_dataset.id is not None

    def test_sets_metadata(self, sample_dataset):
        assert sample_dataset.metadata["name"] == "Test Dataset"

    def test_initializes_empty_datatables(self, sample_dataset):
        from tse_analytics.core.data.dataset import Dataset

        # Create a fresh dataset for this test
        with patch("tse_analytics.core.data.dataset.messaging"):
            ds = Dataset(
                metadata={"name": "Fresh", "description": "d"},
                animals={},
            )
        assert ds.datatables == {}

    def test_initializes_empty_factors(self, sample_dataset):
        assert sample_dataset.factors == {}

    def test_initializes_empty_reports(self, sample_dataset):
        assert sample_dataset.reports == {}

    def test_default_outliers_settings(self, sample_dataset):
        assert sample_dataset.outliers_settings.mode == OutliersMode.OFF
        assert sample_dataset.outliers_settings.coefficient == 1.5

    def test_default_binning_settings(self, sample_dataset):
        assert sample_dataset.binning_settings.apply is False


class TestDatasetProperties:
    """Tests for Dataset properties."""

    def test_name(self, sample_dataset):
        assert sample_dataset.name == "Test Dataset"

    def test_description(self, sample_dataset):
        assert sample_dataset.description == "A test dataset"

    def test_source_path(self, sample_dataset):
        assert sample_dataset.source_path == "/test/path"

    def test_source_path_missing(self):
        from tse_analytics.core.data.dataset import Dataset

        with patch("tse_analytics.core.data.dataset.messaging"):
            ds = Dataset(metadata={"name": "N", "description": "D"}, animals={})
        assert ds.source_path == ""

    def test_experiment_started(self, sample_dataset):
        result = sample_dataset.experiment_started
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2024

    def test_experiment_stopped(self, sample_dataset):
        result = sample_dataset.experiment_stopped
        assert isinstance(result, pd.Timestamp)

    def test_experiment_duration(self, sample_dataset):
        duration = sample_dataset.experiment_duration
        assert isinstance(duration, pd.Timedelta)
        assert duration == pd.Timedelta("5h")


class TestDatasetDatatablesCRUD:
    """Tests for datatable add/remove on Dataset."""

    def test_add_datatable(self, sample_dataset, sample_datatable):
        assert "Main" in sample_dataset.datatables

    def test_remove_datatable(self, sample_dataset, sample_datatable):
        sample_dataset.remove_datatable(sample_datatable)
        assert "Main" not in sample_dataset.datatables

    def test_add_multiple_datatables(self, sample_dataset, sample_datatable, sample_variables, sample_df):
        from tse_analytics.core.data.datatable import Datatable

        dt2 = Datatable(
            dataset=sample_dataset,
            name="Secondary",
            description="Second",
            variables=sample_variables,
            df=sample_df.copy(),
            sampling_interval=pd.Timedelta("1h"),
        )
        sample_dataset.add_datatable(dt2)
        assert len(sample_dataset.datatables) == 2


class TestDatasetRename:
    """Tests for Dataset.rename."""

    def test_rename_updates_metadata(self, sample_dataset):
        sample_dataset.rename("New Name")
        assert sample_dataset.name == "New Name"


class TestExtractLevelsFromProperty:
    """Tests for Dataset.extract_levels_from_property."""

    def test_extracts_levels(self, sample_dataset):
        levels = sample_dataset.extract_levels_from_property("group")
        assert "Control" in levels
        assert "Treatment" in levels

    def test_control_has_correct_animal(self, sample_dataset):
        levels = sample_dataset.extract_levels_from_property("group")
        assert "A1" in levels["Control"].animal_ids

    def test_treatment_has_correct_animals(self, sample_dataset):
        levels = sample_dataset.extract_levels_from_property("group")
        assert "A2" in levels["Treatment"].animal_ids

    def test_nonexistent_property_returns_empty(self, sample_dataset):
        levels = sample_dataset.extract_levels_from_property("nonexistent")
        assert levels == {}


class TestRenameAnimal:
    """Tests for Dataset.rename_animal."""

    def test_renames_in_animals_dict(self, sample_dataset, sample_datatable):
        old_animal = sample_dataset.animals["A1"]
        new_animal = Animal(enabled=True, id="NewA1", color=old_animal.color, properties=old_animal.properties)

        sample_dataset.rename_animal("A1", new_animal)

        assert "NewA1" in sample_dataset.animals
        assert "A1" not in sample_dataset.animals

    def test_renames_in_metadata(self, sample_dataset, sample_datatable):
        old_animal = sample_dataset.animals["A1"]
        new_animal = Animal(enabled=True, id="NewA1", color=old_animal.color, properties=old_animal.properties)

        sample_dataset.rename_animal("A1", new_animal)

        assert "NewA1" in sample_dataset.metadata["animals"]

    def test_renames_in_factor_levels(self, sample_dataset, sample_datatable, sample_factor):
        sample_dataset.factors = {"Group": sample_factor}

        old_animal = sample_dataset.animals["A1"]
        new_animal = Animal(enabled=True, id="NewA1", color=old_animal.color, properties=old_animal.properties)

        sample_dataset.rename_animal("A1", new_animal)

        control_level = sample_factor.levels[0]
        assert "NewA1" in control_level.animal_ids
        assert "A1" not in control_level.animal_ids


class TestExcludeAnimals:
    """Tests for Dataset.exclude_animals."""

    def test_removes_animal_from_dict(self, sample_dataset, sample_datatable):
        sample_dataset.exclude_animals({"A1"})
        assert "A1" not in sample_dataset.animals

    def test_removes_from_metadata(self, sample_dataset, sample_datatable):
        sample_dataset.exclude_animals({"A1"})
        assert "A1" not in sample_dataset.metadata["animals"]

    def test_removes_from_factor_levels(self, sample_dataset, sample_datatable, sample_factor):
        sample_dataset.factors = {"Group": sample_factor}
        sample_dataset.set_factors(sample_dataset.factors)

        sample_dataset.exclude_animals({"A1"})

        control_level = sample_factor.levels[0]
        assert "A1" not in control_level.animal_ids


class TestExcludeAndTrimTime:
    """Tests for Dataset.exclude_time and trim_time."""

    def test_exclude_time_adjusts_start(self, sample_dataset, sample_datatable):
        # Exclude from start to 2hours in
        range_start = pd.Timestamp("2023-12-31")
        range_end = pd.Timestamp("2024-01-01 02:00:00")

        sample_dataset.exclude_time(range_start, range_end)
        assert sample_dataset.experiment_started == pd.Timestamp("2024-01-01 02:00:00")

    def test_trim_time_adjusts_both(self, sample_dataset, sample_datatable):
        sample_dataset.trim_time(
            pd.Timestamp("2024-01-01 01:00:00"),
            pd.Timestamp("2024-01-01 03:00:00"),
        )
        assert sample_dataset.experiment_started == pd.Timestamp("2024-01-01 01:00:00")
        assert sample_dataset.experiment_stopped == pd.Timestamp("2024-01-01 03:00:00")


class TestSetFactors:
    """Tests for Dataset.set_factors."""

    def test_stores_factors(self, sample_dataset, sample_datatable, sample_factor):
        factors = {"Group": sample_factor}
        sample_dataset.set_factors(factors)
        assert "Group" in sample_dataset.factors

    def test_propagates_to_datatables(self, sample_dataset, sample_datatable, sample_factor):
        factors = {"Group": sample_factor}
        sample_dataset.set_factors(factors)
        # The factor column should be added to the original_df
        assert "Group" in sample_datatable.df.columns


class TestApplyBinning:
    """Tests for Dataset.apply_binning."""

    def test_stores_settings(self, sample_dataset):
        from tse_analytics.core import messaging

        settings = BinningSettings()
        settings.apply = True

        with patch.object(messaging, "broadcast"):
            sample_dataset.apply_binning(settings)

        assert sample_dataset.binning_settings.apply is True

    def test_broadcasts_message(self, sample_dataset):
        from tse_analytics.core import messaging

        settings = BinningSettings()

        with patch.object(messaging, "broadcast") as mock_broadcast:
            sample_dataset.apply_binning(settings)

        assert mock_broadcast.called
        call_args = mock_broadcast.call_args[0][0]
        assert isinstance(call_args, messaging.BinningMessage)


class TestApplyOutliers:
    """Tests for Dataset.apply_outliers."""

    def test_stores_settings(self, sample_dataset):
        from tse_analytics.core import messaging

        settings = OutliersSettings(OutliersMode.REMOVE, 2.0)

        with patch.object(messaging, "broadcast"):
            sample_dataset.apply_outliers(settings)

        assert sample_dataset.outliers_settings.mode == OutliersMode.REMOVE

    def test_broadcasts_message(self, sample_dataset):
        from tse_analytics.core import messaging

        settings = OutliersSettings(OutliersMode.REMOVE, 2.0)

        with patch.object(messaging, "broadcast") as mock_broadcast:
            sample_dataset.apply_outliers(settings)

        assert mock_broadcast.called


class TestReports:
    """Tests for Dataset report management."""

    def test_add_report(self, sample_dataset):
        from tse_analytics.core.data.report import Report

        report = Report(dataset=sample_dataset, name="Test Report", content="<h1>Test</h1>")
        sample_dataset.add_report(report)
        assert "Test Report" in sample_dataset.reports

    def test_add_duplicate_report_appends(self, sample_dataset):
        from tse_analytics.core.data.report import Report

        r1 = Report(dataset=sample_dataset, name="Report", content="part1")
        r2 = Report(dataset=sample_dataset, name="Report", content="part2")

        sample_dataset.add_report(r1)
        sample_dataset.add_report(r2)

        assert sample_dataset.reports["Report"].content == "part1part2"

    def test_delete_report(self, sample_dataset):
        from tse_analytics.core.data.report import Report

        report = Report(dataset=sample_dataset, name="ToDelete", content="x")
        sample_dataset.add_report(report)
        sample_dataset.delete_report("ToDelete")

        assert "ToDelete" not in sample_dataset.reports


class TestDatasetClone:
    """Tests for Dataset.clone."""

    def test_clone_returns_deep_copy(self, sample_dataset):
        with patch("tse_analytics.core.data.dataset.messaging"):
            clone = sample_dataset.clone()

        assert clone is not sample_dataset
        assert clone.name == sample_dataset.name

    def test_clone_is_independent(self, sample_dataset):
        with patch("tse_analytics.core.data.dataset.messaging"):
            clone = sample_dataset.clone()

        clone.rename("Cloned")
        assert sample_dataset.name != "Cloned"


class TestDatasetSetstate:
    """Tests for Dataset.__setstate__ (unpickling)."""

    def test_unpickle_restores_state(self, sample_dataset, sample_datatable):
        with patch("tse_analytics.core.data.dataset.messaging"):
            data = pickle.dumps(sample_dataset)
            restored = pickle.loads(data)

        assert restored.name == sample_dataset.name
        assert "Main" in restored.datatables
