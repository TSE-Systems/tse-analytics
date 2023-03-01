from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QDialog, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.factors_dialog import FactorsDialog
from tse_analytics.views.selection.factors.factors_table_view import FactorsTableView
from tse_datatools.data.factor import Factor


class FactorsViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.table_view = FactorsTableView(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)

    def clear(self):
        self.table_view.clear()

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.table_view.set_data(message.data.factors)

    def edit_factors(self):
        dlg = FactorsDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            factors: dict[str, Factor] = {}
            for factor in dlg.factors:
                factors[factor.name] = factor
            Manager.data.selected_dataset.set_factors(factors)
            Manager.messenger.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        edit_factors_action = QAction(QIcon(":/icons/icons8-edit-16.png"), "Edit Factors", toolbar)
        edit_factors_action.triggered.connect(self.edit_factors)
        toolbar.addAction(edit_factors_action)

        return toolbar
