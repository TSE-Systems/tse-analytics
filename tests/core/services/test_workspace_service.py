"""Tests for :class:`WorkspaceService` — lifecycle, persistence formats, cleanup.

``qapp`` is required because ``_cleanup_workspace`` schedules ``gc.collect`` via
``QTimer.singleShot``, which needs a ``QApplication`` to exist.
"""

from tse_analytics.core import messaging
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService


def test_new_workspace_resets_and_broadcasts(qapp, recorder, make_dataset):
    sel = SelectionService()
    svc = WorkspaceService(sel)
    dataset = make_dataset()
    svc.get_workspace().datasets[dataset.id] = dataset
    recorder.messages.clear()

    svc.new_workspace()

    assert svc.get_workspace().datasets == {}
    assert recorder.of_type(messaging.WorkspaceChangedMessage)


def test_duckdb_save_load_delegation(qapp, tmp_path, make_dataset):
    dataset = make_dataset("DS")
    svc = WorkspaceService(SelectionService())
    svc.get_workspace().datasets[dataset.id] = dataset
    path = str(tmp_path / "ws.duckdb")
    svc.save_workspace(path)

    reloaded = WorkspaceService(SelectionService())
    reloaded.load_workspace(path)
    assert len(reloaded.get_workspace().datasets) == 1
    assert next(iter(reloaded.get_workspace().datasets.values())).name == "DS"


def test_legacy_pickle_save_load_roundtrip(qapp, tmp_path, make_dataset):
    dataset = make_dataset("DS")
    svc = WorkspaceService(SelectionService())
    svc.get_workspace().datasets[dataset.id] = dataset
    path = str(tmp_path / "ws.workspace")  # legacy pickle format
    svc.save_workspace(path)

    reloaded = WorkspaceService(SelectionService())
    reloaded.load_workspace(path)
    assert len(reloaded.get_workspace().datasets) == 1
    assert next(iter(reloaded.get_workspace().datasets.values())).name == "DS"


def test_load_clears_prior_selection(qapp, tmp_path, make_dataset):
    dataset = make_dataset("DS")
    sel = SelectionService()
    sel.set_selected_dataset(object())
    svc = WorkspaceService(sel)
    svc.get_workspace().datasets[dataset.id] = dataset
    path = str(tmp_path / "ws.duckdb")
    svc.save_workspace(path)

    svc.load_workspace(path)
    assert sel.get_selected_dataset() is None
