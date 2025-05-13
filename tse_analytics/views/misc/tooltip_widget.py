from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel


class TooltipWidget(QLabel):
    def __init__(self, tooltip: str, parent=None):
        super().__init__(parent)

        self.setPixmap(QIcon(":/icons/help.png").pixmap(16, 16))
        self.setToolTip(tooltip)
