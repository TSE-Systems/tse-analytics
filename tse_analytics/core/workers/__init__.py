"""
Worker thread management module for TSE Analytics.

This module provides classes for managing worker threads in the application,
including thread creation, execution, and signal handling.

Classes:
    Worker: A worker thread that can execute a function in a separate thread.
    TaskManager: Manages worker threads using a thread pool.
    WorkerSignals: Defines signals that can be emitted by worker threads.
"""

from tse_analytics.core.workers.worker import Worker
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker_signals import WorkerSignals

__all__ = ['Worker', 'TaskManager', 'WorkerSignals']
