"""Tests for :class:`DatasetService` — dataset/datatable/report CRUD + broadcasts.

``qapp`` is needed for operations that go through ``_cleanup_workspace`` (QTimer).
"""

from tse_analytics.core import messaging
from tse_analytics.core.data.report import Report
from tse_analytics.core.services.dataset_service import DatasetService
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService


def _services():
    sel = SelectionService()
    ws = WorkspaceService(sel)
    return DatasetService(ws, sel), ws


def test_add_dataset_registers_and_broadcasts(qapp, recorder, make_dataset):
    svc, ws = _services()
    dataset = make_dataset()

    svc.add_dataset(dataset)

    assert dataset.id in ws.get_workspace().datasets
    assert recorder.of_type(messaging.WorkspaceChangedMessage)


def test_remove_dataset(qapp, recorder, make_dataset):
    svc, ws = _services()
    dataset = make_dataset()
    svc.add_dataset(dataset)

    svc.remove_dataset(dataset)

    assert dataset.id not in ws.get_workspace().datasets


def test_clone_dataset_adds_independent_copy(qapp, recorder, make_dataset):
    svc, ws = _services()
    dataset = make_dataset("Original")
    svc.add_dataset(dataset)

    svc.clone_dataset(dataset, "Cloned")

    names = sorted(d.name for d in ws.get_workspace().datasets.values())
    assert names == ["Cloned", "Original"]
    ids = [d.id for d in ws.get_workspace().datasets.values()]
    assert len(set(ids)) == 2  # clone got a fresh id


def test_add_and_remove_datatable(qapp, recorder, make_dataset):
    svc, _ = _services()
    dataset = make_dataset()
    svc.add_dataset(dataset)

    extra = dataset.datatables["Main"].clone()
    extra.name = "Copy"
    svc.add_datatable(extra)
    assert "Copy" in dataset.datatables

    svc.remove_datatable(extra)
    assert "Copy" not in dataset.datatables


def test_add_report_broadcasts(qapp, recorder, make_dataset):
    svc, _ = _services()
    dataset = make_dataset()
    svc.add_dataset(dataset)

    svc.add_report(Report(dataset, "R2", "<p>x</p>"))

    assert "R2" in dataset.reports
    assert recorder.of_type(messaging.ReportsChangedMessage)


def test_delete_report_broadcasts(qapp, recorder, make_dataset):
    svc, _ = _services()
    dataset = make_dataset()
    svc.add_dataset(dataset)
    svc.add_report(Report(dataset, "R2", "<p>x</p>"))

    svc.delete_report(Report(dataset, "R2", "<p>x</p>"))

    assert "R2" not in dataset.reports
    assert recorder.of_type(messaging.ReportsChangedMessage)
