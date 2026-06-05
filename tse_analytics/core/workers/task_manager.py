"""
Task management module for handling concurrent operations.

This module provides the TaskManager class for managing worker threads
using a thread pool to execute tasks concurrently.
"""

from loguru import logger
from PySide6.QtCore import QObject, QThread, QThreadPool

from tse_analytics.core.workers.worker import Worker


class TaskManager(QObject):
    """
    Manages worker threads using a thread pool.

    This class provides a centralized way to manage worker threads in the application.
    It initializes a thread pool and provides methods to start worker tasks with
    specified priorities.

    A single instance must be constructed during application bootstrap (see
    ``tse_analytics/main.py``) before any task is submitted; the thread pool is held as
    class-level state and shared by the ``start_task`` classmethod.

    Attributes:
        threadpool (QThreadPool | None): The thread pool used to manage worker threads.
    """

    threadpool: QThreadPool | None = None

    def __init__(self, parent: QObject):
        """
        Initialize the TaskManager with a new thread pool.

        Args:
            parent (QObject): The parent QObject that owns the thread pool, ensuring it
                is destroyed (and pending tasks awaited) together with the application.
        """
        super().__init__(parent)
        TaskManager.threadpool = QThreadPool(self)
        logger.info(f"Multithreading with maximum {TaskManager.threadpool.maxThreadCount()} threads")

    @classmethod
    def start_task(cls, worker: Worker, priority: QThread.Priority = QThread.Priority.IdlePriority) -> None:
        """
        Start a worker task with the specified priority.

        Args:
            worker (Worker): The worker to execute.
            priority (QThread.Priority, optional): The priority of the task.
                Defaults to QThread.Priority.IdlePriority.

        Raises:
            RuntimeError: If the TaskManager has not been initialized yet (no instance
                was constructed during bootstrap).
        """
        if cls.threadpool is None:
            raise RuntimeError(
                "TaskManager is not initialized; construct a TaskManager instance before starting tasks."
            )
        cls.threadpool.start(worker, priority.value)

    @classmethod
    def wait_for_done(cls, timeout_ms: int = -1) -> bool:
        """
        Block until all running and queued tasks have finished.

        Useful for deterministic teardown in tests and for graceful shutdown.

        Args:
            timeout_ms (int, optional): Maximum time to wait in milliseconds. A negative
                value (the default) waits indefinitely.

        Returns:
            bool: ``True`` if all tasks finished, ``False`` if the timeout elapsed first.
        """
        if cls.threadpool is None:
            return True
        return cls.threadpool.waitForDone(timeout_ms)
