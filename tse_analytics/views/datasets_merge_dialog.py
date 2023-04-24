from typing import Optional

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.datasets_merge_dialog_ui import Ui_DatasetsMergeDialog


class DatasetsMergeDialog(QDialog, Ui_DatasetsMergeDialog):
    """Datasets Merge Dialog"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
