"""Tests for the analysis-log persistence and replay surface."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest
from tse_analytics.core.data.analysis_log import (
    CreateDerivedDatatableAction,
    ExcludeAnimalsAction,
    SetFactorsAction,
)
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import Factor, FactorLevel
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.io.storage import load_workspace, save_workspace


def _build_actions() -> list:
    return [
        ExcludeAnimalsAction(
            timestamp=datetime(2026, 4, 28, 10, 0, 0),
            sequence=0,
            description="Excluded animals: A3",
            animal_ids=["A3"],
        ),
        SetFactorsAction(
            timestamp=datetime(2026, 4, 28, 10, 5, 0),
            sequence=1,
            description="Set factors: Group",
            factors={
                "Group": Factor(
                    name="Group",
                    levels=[
                        FactorLevel(name="Control", color="#FF0000", animal_ids=["A1"]),
                        FactorLevel(name="Treatment", color="#00FF00", animal_ids=["A2"]),
                    ],
                )
            },
        ),
        CreateDerivedDatatableAction(
            timestamp=datetime(2026, 4, 28, 10, 10, 0),
            sequence=2,
            description="Derived 'Hourly' from 'Main'",
            source_datatable_name="Main",
            target_datatable_name="Hourly",
            target_description="hourly bins",
            excluded_animal_ids=[],
            binning=TimeIntervalsBinningSettings(unit="hour", delta=1),
        ),
    ]


class TestAnalysisLogPersistence:
    def test_round_trip(self, sample_dataset, sample_datatable, tmp_path):
        sample_dataset.analysis_log = _build_actions()

        workspace = Workspace(name="test_ws")
        workspace.datasets[sample_dataset.id] = sample_dataset

        out_path = tmp_path / "round_trip.duckdb"
        with patch("tse_analytics.core.data.dataset.messaging"):
            save_workspace(str(out_path), workspace)
            loaded = load_workspace(str(out_path))

        loaded_dataset = loaded.datasets[sample_dataset.id]
        assert len(loaded_dataset.analysis_log) == 3
        kinds = [a.kind for a in loaded_dataset.analysis_log]
        assert kinds == ["exclude_animals", "set_factors", "create_derived_datatable"]

    def test_sequences_preserved(self, sample_dataset, sample_datatable, tmp_path):
        sample_dataset.analysis_log = _build_actions()

        workspace = Workspace(name="test_ws")
        workspace.datasets[sample_dataset.id] = sample_dataset

        out_path = tmp_path / "sequences.duckdb"
        with patch("tse_analytics.core.data.dataset.messaging"):
            save_workspace(str(out_path), workspace)
            loaded = load_workspace(str(out_path))

        loaded_dataset = loaded.datasets[sample_dataset.id]
        sequences = [a.sequence for a in loaded_dataset.analysis_log]
        assert sequences == [0, 1, 2]

    def test_payloads_preserved(self, sample_dataset, sample_datatable, tmp_path):
        sample_dataset.analysis_log = _build_actions()

        workspace = Workspace(name="test_ws")
        workspace.datasets[sample_dataset.id] = sample_dataset

        out_path = tmp_path / "payload.duckdb"
        with patch("tse_analytics.core.data.dataset.messaging"):
            save_workspace(str(out_path), workspace)
            loaded = load_workspace(str(out_path))

        loaded_dataset = loaded.datasets[sample_dataset.id]
        binning_action = loaded_dataset.analysis_log[2]
        assert binning_action.kind == "create_derived_datatable"
        assert binning_action.binning is not None
        assert binning_action.binning.unit == "hour"
        assert binning_action.binning.delta == 1

    def test_empty_log_round_trip(self, sample_dataset, sample_datatable, tmp_path):
        sample_dataset.analysis_log = []

        workspace = Workspace(name="test_ws")
        workspace.datasets[sample_dataset.id] = sample_dataset

        out_path = tmp_path / "empty.duckdb"
        with patch("tse_analytics.core.data.dataset.messaging"):
            save_workspace(str(out_path), workspace)
            loaded = load_workspace(str(out_path))

        loaded_dataset = loaded.datasets[sample_dataset.id]
        assert loaded_dataset.analysis_log == []


@pytest.fixture
def dataset_with_log(sample_dataset, sample_datatable):
    sample_dataset.analysis_log = _build_actions()
    return sample_dataset


class TestNotebookExport:
    def test_writes_valid_notebook(self, dataset_with_log, tmp_path):
        import nbformat
        from tse_analytics.core.export.notebook_exporter import export_dataset_as_notebook

        out_path = tmp_path / "nb.ipynb"
        export_dataset_as_notebook(dataset_with_log, out_path)

        notebook = nbformat.read(str(out_path), as_version=4)
        nbformat.validate(notebook)

    def test_cell_count(self, dataset_with_log, tmp_path):
        import nbformat
        from tse_analytics.core.export.notebook_exporter import export_dataset_as_notebook

        out_path = tmp_path / "nb_cells.ipynb"
        export_dataset_as_notebook(dataset_with_log, out_path)
        notebook = nbformat.read(str(out_path), as_version=4)

        # 1 markdown header + imports + load + 3 actions + final = 7
        assert len(notebook.cells) == 7

    def test_action_cells_contain_expected_calls(self, dataset_with_log, tmp_path):
        import nbformat
        from tse_analytics.core.export.notebook_exporter import export_dataset_as_notebook

        out_path = tmp_path / "nb_calls.ipynb"
        export_dataset_as_notebook(dataset_with_log, out_path)
        notebook = nbformat.read(str(out_path), as_version=4)

        sources = "\n".join(cell.source for cell in notebook.cells)
        assert "dataset.exclude_animals" in sources
        assert "dataset.set_factors" in sources
        assert "process_table" in sources
        assert "TimeIntervalsBinningSettings" in sources
