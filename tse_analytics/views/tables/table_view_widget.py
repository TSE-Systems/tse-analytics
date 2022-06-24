from inspect import getmembers
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QComboBox

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

    def _show_scale_bar(self, state: bool):
        self.table_view.show_scale_bar(state)

    def _show_mask(self, state: bool):
        self.table_view.show_mask(state)

    def _blend_current_text_changed(self, text: str):
        self.table_view.set_blend_mode(text)

    def _on_binning_applied(self, message: BinningAppliedMessage):
        self.table_view.apply_binning(message)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        label = QLabel("Blend:")
        toolbar.addWidget(label)

        blend_combo_box = QComboBox()
        modes_list = [o for o in getmembers(QPainter) if o[0].startswith('CompositionMode_')]
        blend_combo_box.addItems([f[0].replace('CompositionMode_', '') for f in modes_list])
        blend_combo_box.setCurrentText('Screen')
        blend_combo_box.currentTextChanged.connect(self._blend_current_text_changed)
        toolbar.addWidget(blend_combo_box)

        toolbar.addSeparator()

        show_scale_bar_action = QAction(QIcon(":/icons/icons8-ruler-16.png"), "Scale Bar", self)
        show_scale_bar_action.triggered.connect(self._show_scale_bar)
        show_scale_bar_action.setCheckable(True)
        toolbar.addAction(show_scale_bar_action)

        show_mask_action = QAction(QIcon(":/icons/icons8-ruler-16.png"), "Mask", self)
        show_mask_action.triggered.connect(self._show_mask)
        show_mask_action.setCheckable(True)
        toolbar.addAction(show_mask_action)

        return toolbar
