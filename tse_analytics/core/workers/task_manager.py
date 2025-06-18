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

    Attributes:
        threadpool (QThreadPool | None): The thread pool used to manage worker threads.
    """

    threadpool: QThreadPool | None = None

    def __init__(self, parent: QObject | None = None):
        """
        Initialize the TaskManager with a new thread pool.

        Args:
            parent (QObject | None, optional): The parent QObject. Defaults to None.
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
        """
        cls.threadpool.start(worker, priority.value)
