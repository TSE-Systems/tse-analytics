from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.settings.binning_widget import BinningWidget


class SettingsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.binning_widget = BinningWidget(self)
        self.tab_widget.addTab(self.binning_widget, QIcon(":/icons/icons8-time-span-16.png"), 'Binning')
