"""
Unit tests for tse_analytics.core.help_manager module.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from tse_analytics.core.help_manager import (
    show_online_help,
    show_offline_help,
    close_help_server,
)


class TestShowOnlineHelp:
    """Tests for show_online_help function."""

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    def test_opens_online_documentation_url(self, mock_open_url):
        """Test that show_online_help opens the online documentation URL."""
        show_online_help()

        mock_open_url.assert_called_once_with(
            "https://tse-systems.github.io/tse-analytics-docs"
        )

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    def test_calls_open_url_once(self, mock_open_url):
        """Test that show_online_help calls openUrl exactly once."""
        show_online_help()

        assert mock_open_url.call_count == 1


class TestShowOfflineHelp:
    """Tests for show_offline_help function."""

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', False)
    @patch('tse_analytics.core.help_manager.sys.executable', '/usr/bin/python')
    def test_starts_http_server_when_not_running(
        self,
        mock_popen,
        mock_open_url,
    ):
        """Test that show_offline_help starts HTTP server if not already running."""
        # Reset the global variable
        import tse_analytics.core.help_manager as hm
        hm._help_server_process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        show_offline_help()

        assert mock_popen.called

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', False)
    def test_opens_localhost_url(self, mock_popen, mock_open_url):
        """Test that show_offline_help opens localhost URL."""
        import tse_analytics.core.help_manager as hm
        hm._help_server_process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        show_offline_help()

        mock_open_url.assert_called_with("http://localhost:8000")

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', False)
    def test_does_not_restart_server_if_already_running(
        self,
        mock_popen,
        mock_open_url,
    ):
        """Test that show_offline_help doesn't restart server if already running."""
        import tse_analytics.core.help_manager as hm

        # Simulate server already running
        mock_existing_process = MagicMock()
        hm._help_server_process = mock_existing_process

        show_offline_help()

        # Popen should not be called since server is already running
        mock_popen.assert_not_called()
        # But URL should still be opened
        mock_open_url.assert_called_once()

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', False)
    @patch('tse_analytics.core.help_manager.sys.executable', '/usr/bin/python3')
    def test_uses_correct_python_executable_in_dev(
        self,
        mock_popen,
        mock_open_url,
    ):
        """Test that show_offline_help uses sys.executable in development mode."""
        import tse_analytics.core.help_manager as hm
        hm._help_server_process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        show_offline_help()

        # Check that the command includes sys.executable
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == '/usr/bin/python3'

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', True)
    def test_uses_python_command_in_release(self, mock_popen, mock_open_url):
        """Test that show_offline_help uses 'python' command in release mode."""
        import tse_analytics.core.help_manager as hm
        hm._help_server_process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        show_offline_help()

        # Check that the command uses 'python'
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == 'python'

    @patch('tse_analytics.core.help_manager.QDesktopServices.openUrl')
    @patch('tse_analytics.core.help_manager.subprocess.Popen')
    @patch('tse_analytics.core.help_manager.IS_RELEASE', False)
    def test_http_server_command_arguments(self, mock_popen, mock_open_url):
        """Test that show_offline_help passes correct arguments to http.server."""
        import tse_analytics.core.help_manager as hm
        hm._help_server_process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        show_offline_help()

        # Check the command arguments
        call_args = mock_popen.call_args[0][0]
        assert "-m" in call_args
        assert "http.server" in call_args
        assert "-d" in call_args


class TestCloseHelpServer:
    """Tests for close_help_server function."""

    def test_kills_server_process_if_running(self):
        """Test that close_help_server kills the server process if running."""
        import tse_analytics.core.help_manager as hm

        mock_process = MagicMock()
        hm._help_server_process = mock_process

        close_help_server()

        mock_process.kill.assert_called_once()

    def test_sets_process_to_none_after_killing(self):
        """Test that close_help_server sets _help_server_process to None."""
        import tse_analytics.core.help_manager as hm

        mock_process = MagicMock()
        hm._help_server_process = mock_process

        close_help_server()

        assert hm._help_server_process is None

    def test_does_nothing_if_server_not_running(self):
        """Test that close_help_server does nothing if server is not running."""
        import tse_analytics.core.help_manager as hm

        hm._help_server_process = None

        # Should not raise any errors
        close_help_server()

        assert hm._help_server_process is None

    def test_can_be_called_multiple_times(self):
        """Test that close_help_server can be called multiple times safely."""
        import tse_analytics.core.help_manager as hm

        mock_process = MagicMock()
        hm._help_server_process = mock_process

        close_help_server()
        close_help_server()  # Second call should not raise an error

        assert hm._help_server_process is None
