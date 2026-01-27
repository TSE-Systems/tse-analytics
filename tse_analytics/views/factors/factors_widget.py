from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QToolBar, QTreeView, QVBoxLayout, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Factor
from tse_analytics.core.models.color_dialog_delegate import ColorDialogDelegate
from tse_analytics.core.models.factors_model import FactorsModel
from tse_analytics.views.factors.factors_dialog import FactorsDialog


class FactorsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.dataset: Dataset | None = None

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar(
            "Factors Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.edit_factors_action = toolbar.addAction(QIcon(":/icons/icons8-edit-16.png"), "Edit Factors")
        self.edit_factors_action.triggered.connect(self._edit_factors)
        self.edit_factors_action.setEnabled(False)

        self._layout.addWidget(toolbar)

        self.treeView = QTreeView(
            self,
            headerHidden=True,
        )
        self.treeView.setItemDelegate(ColorDialogDelegate(self.treeView))
        self._layout.addWidget(self.treeView)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self.dataset = None
            self.edit_factors_action.setEnabled(False)
            self.treeView.setModel(None)
        else:
            self.dataset = message.dataset
            model = FactorsModel(self.dataset.factors, self)
            self.treeView.setModel(model)
            self.treeView.expandAll()
            self.edit_factors_action.setEnabled(True)

    def _edit_factors(self):
        dlg = FactorsDialog(self.dataset, self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            factors: dict[str, Factor] = {}
            for factor in dlg.factors:
                factors[factor.name] = factor
            self.dataset.set_factors(factors)
            messaging.broadcast(messaging.DatasetChangedMessage(self, self.dataset))
