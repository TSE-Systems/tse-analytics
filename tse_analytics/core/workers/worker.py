"""
Worker thread implementation module.

This module provides the Worker class for executing functions in separate threads
with signal handling for results, errors and completion status.
"""

import sys
import traceback

from PySide6.QtCore import QRunnable, Slot

from tse_analytics.core.workers.worker_signals import WorkerSignals


class Worker(QRunnable):
    """
    Worker thread for executing functions asynchronously.

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    The worker executes the provided function in a separate thread and emits
    signals for result, error, and completion status.

    Attributes:
        fn: The function to execute in the worker thread.
        args: Positional arguments to pass to the function.
        kwargs: Keyword arguments to pass to the function.
        signals (WorkerSignals): Signals for communicating with the main thread.

    Args:
        fn: The function callback to run on this worker thread. Supplied args and
            kwargs will be passed through to the runner.
        *args: Arguments to pass to the callback function.
        **kwargs: Keywords to pass to the callback function.
    """

    def __init__(self, fn, *args, **kwargs):
        """
        Initialize the worker with a function and its arguments.

        Args:
            fn: The function to execute in the worker thread.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        """
        Execute the function in the worker thread.

        This method is called when the worker is started. It executes the function
        with the provided arguments and emits signals based on the outcome:
        - result signal with the function's return value on success
        - error signal with exception information on failure
        - finished signal when execution is complete (in both success and failure cases)
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
