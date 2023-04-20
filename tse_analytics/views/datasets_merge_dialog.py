from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QInputDialog, QListWidgetItem, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.datasets_merge_dialog_ui import Ui_DatasetsMergeDialog
from tse_datatools.data.factor import Factor
from tse_datatools.data.group import Group


class DatasetsMergeDialog(QDialog, Ui_DatasetsMergeDialog):
    """Datasets Merge Dialog"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
