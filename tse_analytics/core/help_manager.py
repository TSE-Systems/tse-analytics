import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtGui import QDesktopServices

from tse_analytics.core.utils import IS_RELEASE

_help_server_process: subprocess.Popen | None = None


def show_online_help():
    QDesktopServices.openUrl("https://tse-systems.github.io/tse-analytics-docs")


def show_offline_help():
    global _help_server_process

    if _help_server_process is None:
        current_directory = Path.cwd()
        docs_directory = current_directory / "_internal/docs" if IS_RELEASE else current_directory.parent / "docs"

        # python_executable = "_internal/python.exe" if IS_RELEASE else sys.executable
        python_executable = "python" if IS_RELEASE else sys.executable

        startupinfo = None
        if IS_RELEASE and os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        _help_server_process = subprocess.Popen(
            [python_executable, "-m", "http.server", "-d", str(docs_directory)],
            shell=False,
            stdin=None,
            stdout=None,
            stderr=None,
            close_fds=True,
            startupinfo=startupinfo,
        )

    QDesktopServices.openUrl("http://localhost:8000")


def close_help_server():
    global _help_server_process
    if _help_server_process is not None:
        _help_server_process.kill()
        _help_server_process = None
