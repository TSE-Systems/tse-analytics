"""Tests for :class:`SelectionService` — selection state and change broadcasts."""

from tse_analytics.core import messaging
from tse_analytics.core.services.selection_service import SelectionService


def test_set_and_get_selected_dataset(recorder):
    svc = SelectionService()
    assert svc.get_selected_dataset() is None

    dataset = object()
    svc.set_selected_dataset(dataset)
    assert svc.get_selected_dataset() is dataset

    messages = recorder.of_type(messaging.DatasetChangedMessage)
    assert len(messages) == 1
    assert messages[0].dataset is dataset


def test_set_and_get_selected_datatable(recorder):
    svc = SelectionService()
    datatable = object()
    svc.set_selected_datatable(datatable)
    assert svc.get_selected_datatable() is datatable

    messages = recorder.of_type(messaging.DatatableChangedMessage)
    assert len(messages) == 1
    assert messages[0].datatable is datatable


def test_clear_resets_both_and_broadcasts_none(recorder):
    svc = SelectionService()
    svc.set_selected_dataset(object())
    svc.set_selected_datatable(object())
    recorder.messages.clear()

    svc.clear()

    assert svc.get_selected_dataset() is None
    assert svc.get_selected_datatable() is None
    # clear() nulls the datatable first, then the dataset.
    assert [m.datatable for m in recorder.of_type(messaging.DatatableChangedMessage)] == [None]
    assert [m.dataset for m in recorder.of_type(messaging.DatasetChangedMessage)] == [None]
