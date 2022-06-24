from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from tse_analytics.messaging.messages import AnimalDataChangedMessage


class ChannelsSettingsWidget(QWidget):
    def __init__(self, parent=None, blend_view=None):
        super().__init__(parent)
        self.blend_view = blend_view

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def clear(self):
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def set_data(self, message: AnimalDataChangedMessage):
        self.clear()
        # for item in message.images:
        #     item_widget = ChannelSettingsWidget(self, item, self.blend_view)
        #     self.layout().addWidget(item_widget)
