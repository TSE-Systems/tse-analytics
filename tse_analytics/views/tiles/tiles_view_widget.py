from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import AnimalDataChangedMessage, DatasetRemovedMessage, DatasetUnloadedMessage
from tse_analytics.views.tiles.tiles_view import TilesView


class TilesViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.tiles_view = TilesView(self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.tiles_view)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, AnimalDataChangedMessage, self._on_channel_images_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_slide_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_slide_unloaded)

    def clear(self):
        self.tiles_view.clear()

    def _on_slide_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_slide_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _on_channel_images_changed(self, message: AnimalDataChangedMessage):
        self.tiles_view.set_data(message.animals)

    def fit_all_tiles(self):
        self.tiles_view.fit_all_tiles()

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        fit_all_tiles_action = QAction(QIcon(":/icons/grid.png"), "Fit All Tiles", self)
        fit_all_tiles_action.triggered.connect(self.fit_all_tiles)
        toolbar.addAction(fit_all_tiles_action)

        return toolbar
