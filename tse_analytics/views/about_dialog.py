import importlib.metadata
import subprocess
from typing import Optional

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.about_dialog_ui import Ui_AboutDialog


def start_process_ps_v2():
    ps_args = "-Command (Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"

    cmd = ["powershell", *ps_args.split(" ")]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, _ = proc.communicate(timeout=120)

    raw_output = out.decode("utf-8").strip()
    return raw_output


class AboutDialog(QDialog, Ui_AboutDialog):
    """About Dialog"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        version = importlib.metadata.version("tse-analytics")
        self.labelVersion.setText(f"Version: {version}")

        hardware_id = start_process_ps_v2()
        self.lineEditHardwareId.setText(hardware_id)
