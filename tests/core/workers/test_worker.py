"""
Unit tests for tse_analytics.core.workers.worker module.

The worker is driven synchronously via ``run()`` so the result/error/finished
contract can be asserted deterministically without an event loop.
"""

from unittest.mock import patch

from tse_analytics.core.workers.worker import Worker


class TestWorkerSuccess:
    """Tests for the success path."""

    def test_result_emitted_with_return_value(self, qapp):
        """result fires with the function's return value."""
        results = []
        worker = Worker(lambda x, y: x + y, 2, 3)
        worker.signals.result.connect(results.append)

        worker.run()

        assert results == [5]

    def test_kwargs_passed_through(self, qapp):
        """Keyword arguments are forwarded to the wrapped function."""
        results = []
        worker = Worker(lambda a, b=0: a + b, 1, b=4)
        worker.signals.result.connect(results.append)

        worker.run()

        assert results == [5]

    def test_finished_emitted_on_success(self, qapp):
        """finished fires once on the success path."""
        finished = []
        worker = Worker(lambda: 42)
        worker.signals.finished.connect(lambda: finished.append(True))

        worker.run()

        assert finished == [True]


class TestWorkerFailure:
    """Tests for the exception path."""

    @staticmethod
    def _boom():
        raise ValueError("kaboom")

    def test_error_emitted_with_three_tuple(self, qapp):
        """error fires with (exc_type, exc_value, traceback_string)."""
        errors = []
        worker = Worker(self._boom)
        worker.signals.error.connect(errors.append)

        with patch("tse_analytics.core.workers.worker.logger"):
            worker.run()

        assert len(errors) == 1
        exc_type, exc_value, tb_str = errors[0]
        assert exc_type is ValueError
        assert isinstance(exc_value, ValueError)
        assert "kaboom" in tb_str

    def test_result_not_emitted_on_exception(self, qapp):
        """result does not fire when the function raises."""
        results = []
        worker = Worker(self._boom)
        worker.signals.result.connect(results.append)

        with patch("tse_analytics.core.workers.worker.logger"):
            worker.run()

        assert results == []

    def test_finished_emitted_on_exception(self, qapp):
        """finished still fires when the function raises."""
        finished = []
        worker = Worker(self._boom)
        worker.signals.finished.connect(lambda: finished.append(True))

        with patch("tse_analytics.core.workers.worker.logger"):
            worker.run()

        assert finished == [True]

    def test_exception_logged_via_loguru(self, qapp):
        """Failures are reported through the loguru sink."""
        worker = Worker(self._boom)

        with patch("tse_analytics.core.workers.worker.logger") as mock_logger:
            worker.run()

        mock_logger.opt.assert_called_once()
        mock_logger.opt.return_value.error.assert_called_once()
