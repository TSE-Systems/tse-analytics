"""
Unit tests for tse_analytics.core.workers.task_manager module.
"""

import threading

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker


@pytest.fixture(scope="module")
def qapp():
    """Create a QApplication instance for Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def reset_threadpool():
    """Snapshot and restore the class-level thread pool around each test."""
    original = TaskManager.threadpool
    yield
    TaskManager.threadpool = original


class TestTaskManager:
    """Tests for TaskManager initialization and task dispatch."""

    def test_start_task_raises_when_uninitialized(self, qapp, reset_threadpool):
        """A clear error is raised if no TaskManager instance was constructed."""
        TaskManager.threadpool = None
        worker = Worker(lambda: None)

        with pytest.raises(RuntimeError, match="not initialized"):
            TaskManager.start_task(worker)

    def test_initialization_sets_threadpool(self, qapp, reset_threadpool):
        """Constructing a TaskManager populates the shared thread pool."""
        parent = QObject()
        TaskManager(parent)

        assert TaskManager.threadpool is not None

    def test_start_task_runs_worker(self, qapp, reset_threadpool):
        """A submitted worker actually executes on the pool."""
        parent = QObject()
        TaskManager(parent)

        done = threading.Event()
        worker = Worker(done.set)
        TaskManager.start_task(worker)

        assert TaskManager.wait_for_done(5000)
        assert done.is_set()

    def test_wait_for_done_returns_true_without_pool(self, reset_threadpool):
        """wait_for_done is a no-op (True) when no pool exists."""
        TaskManager.threadpool = None

        assert TaskManager.wait_for_done() is True
