from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QWidget
from pyqtgraph import GraphicsView

from tse_analytics.views.settings.histogram_view import HistogramView


class ChannelSettingsWidget(QWidget):
    def __init__(self, parent, image_item: any, blend_view):
        super().__init__(parent)

        self.image_item = image_item
        self.blend_view = blend_view

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        groupbox = QGroupBox(image_item.channel.label)
        layout.addWidget(groupbox)

        groupbox_layout = QVBoxLayout()
        groupbox_layout.setContentsMargins(0, 0, 0, 0)
        groupbox_layout.setSpacing(0)
        groupbox.setLayout(groupbox_layout)

        graphics_view = GraphicsView(self)
        histogram_view = HistogramView(image_item, blend_view)
        graphics_view.setCentralItem(histogram_view)
        groupbox_layout.addWidget(graphics_view)
