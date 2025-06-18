"""
Worker signals module for thread communication.

This module provides the WorkerSignals class that defines signals for
communicating between worker threads and the main thread.
"""

from PySide6.QtCore import QObject, Signal


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    This class provides a set of Qt signals that can be used to communicate
    between worker threads and the main thread. These signals are used by
    the Worker class to report results, errors, and progress updates.

    Attributes:
        finished (Signal): Emitted when the worker has completed its task.
            No data is passed with this signal.

        error (Signal): Emitted when an exception occurs in the worker.
            Passes a tuple containing (exception_type, exception_value, traceback_string).

        result (Signal): Emitted when the worker successfully completes its task.
            Passes the return value from the worker function.

        progress (Signal): Emitted to report progress updates from the worker.
            Passes an integer indicating percentage of completion (0-100).
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
