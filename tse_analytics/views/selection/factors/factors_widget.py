from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QToolBar, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import Factor
from tse_analytics.core.models.factors_model import FactorsModel
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.factors_dialog import FactorsDialog
from tse_analytics.views.selection.factors.factors_widget_ui import Ui_FactorsWidget


class FactorsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_FactorsWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        toolbar = QToolBar("Factors Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.edit_factors_action = toolbar.addAction(QIcon(":/icons/icons8-edit-16.png"), "Edit Factors")
        self.edit_factors_action.triggered.connect(self._edit_factors)
        self.edit_factors_action.setEnabled(False)

        self.layout().insertWidget(0, toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)

        self.dataset: Dataset | None = None

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self.dataset = None
            self.edit_factors_action.setEnabled(False)
            self.ui.tableView.model().setSourceModel(None)
        else:
            self.dataset = message.dataset
            model = FactorsModel(list(self.dataset.factors.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()
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
