from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.data.shared import Factor
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.factors_model import FactorsModel
from tse_analytics.views.factors_dialog import FactorsDialog
from tse_analytics.views.selection.factors.factors_widget_ui import Ui_FactorsWidget


class FactorsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_FactorsWidget()
        self.ui.setupUi(self)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)

        self.ui.toolButtonEditFactors.clicked.connect(self._edit_factors)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = FactorsModel(list(message.data.factors.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def _edit_factors(self):
        dlg = FactorsDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            factors: dict[str, Factor] = {}
            for factor in dlg.factors:
                factors[factor.name] = factor
            Manager.data.selected_dataset.set_factors(factors)
            Manager.messenger.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))
