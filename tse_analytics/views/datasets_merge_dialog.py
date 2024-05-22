from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.datasets_merge_dialog_ui import Ui_DatasetsMergeDialog


class DatasetsMergeDialog(QDialog, Ui_DatasetsMergeDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)
