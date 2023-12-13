from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel, QItemSelection
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.models.factors_model import FactorsModel
from tse_analytics.views.factors_dialog import FactorsDialog
from tse_analytics.views.selection.factors.factors_widget_ui import Ui_FactorsWidget
from tse_datatools.data.factor import Factor


class FactorsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_FactorsWidget()
        self.ui.setupUi(self)

        pal = self.ui.tableView.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.ui.tableView.setPalette(pal)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.ui.tableView.selectionModel().selectionChanged.connect(self.__on_selection_changed)

        self.ui.toolButtonEditFactors.clicked.connect(self.__edit_factors)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = FactorsModel(list(message.data.factors.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def __edit_factors(self):
        dlg = FactorsDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            factors: dict[str, Factor] = {}
            for factor in dlg.factors:
                factors[factor.name] = factor
            Manager.data.selected_dataset.set_factors(factors)
            Manager.messenger.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.ui.tableView.model()
        model = proxy_model.sourceModel()
        selected_factors: list[Factor] = []
        for index in self.ui.tableView.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                factor = model.items[row]
                selected_factors.append(factor)
        Manager.data.set_selected_factor(selected_factors[0] if len(selected_factors) > 0 else None)
