import importlib.metadata

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.about_dialog_ui import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        version = importlib.metadata.version("tse-analytics")
        self.labelVersion.setText(f"Version: {version}")
