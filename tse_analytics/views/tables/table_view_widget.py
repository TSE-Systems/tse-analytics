from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetUnloadedMessage, DatasetComponentChangedMessage, \
    BinningAppliedMessage, AnimalDataChangedMessage
from tse_analytics.views.tables.table_view import TableView


class TableViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.table_view = TableView(self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.table_view)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetComponentChangedMessage, self._on_dataset_component_changed)
        messenger.subscribe(self, AnimalDataChangedMessage, self._on_animal_data_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_dataset_unloaded)
        messenger.subscribe(self, BinningAppliedMessage, self._on_binning_applied)

    def clear(self):
        self.table_view.clear()

    def _on_dataset_component_changed(self, message: DatasetComponentChangedMessage):
        self.table_view.set_data(message.data)

    def _on_animal_data_changed(self, message: AnimalDataChangedMessage):
        self.table_view.set_animal_data(message.animals)

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_dataset_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _enable_sorting(self, state: bool):
        self.table_view.set_sorting(state)

    def _on_binning_applied(self, message: BinningAppliedMessage):
        self.table_view.apply_binning(message)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        enable_sorting_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Enable Sorting", self)
        enable_sorting_action.triggered.connect(self._enable_sorting)
        enable_sorting_action.setCheckable(True)
        toolbar.addAction(enable_sorting_action)

        return toolbar
