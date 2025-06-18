import importlib.metadata

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.general.about.about_dialog_ui import Ui_AboutDialog

"""
About dialog module for TSE Analytics.

This module provides a dialog for displaying information about the application,
including its version number.
"""


class AboutDialog(QDialog, Ui_AboutDialog):
    """
    Dialog for displaying information about the application.

    This dialog shows details about the TSE Analytics application, including
    its version number, copyright information, and other relevant details.
    """

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize the AboutDialog with optional parent widget.

        Args:
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)

        version = importlib.metadata.version("tse-analytics")
        self.labelVersion.setText(f"Version {version}")
