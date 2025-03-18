import subprocess
import sys

from PySide6.QtGui import QDesktopServices


def show_online_help():
    QDesktopServices.openUrl("https://tse-systems.github.io/tse-analytics-docs")


def show_offline_help():
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "-d", "c:/docs/"],
        shell=True,
        stdin=None,
        stdout=None,
        stderr=None,
        close_fds=True,
    )

    QDesktopServices.openUrl("http://localhost:8000")
