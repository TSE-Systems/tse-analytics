from PySide6.QtCore import QAbstractAnimation, QEvent, QObject, QPoint, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class Notification(QWidget):
    def __init__(self, text: str, parent: QWidget, duration=None):
        super().__init__(parent)

        self._parent = parent
        self._parent.installEventFilter(self)
        self.installEventFilter(self)
        self._duration = duration
        self._opacity = 0.8
        self._foregroundColor = "#EEEEEE"
        self._backgroundColor = "#444444"

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        # text in toast (toast foreground)
        self._label = QLabel(text)
        self._label.setObjectName("popupLbl")
        self._label.setStyleSheet("QLabel#popupLbl {{ color: #EEEEEE; padding: 5px; }}")

        self._label.setMinimumWidth(min(200, self._label.fontMetrics().boundingRect(text).width() * 2))
        self._label.setMinimumHeight(self._label.fontMetrics().boundingRect(text).height() * 2)
        self._label.setWordWrap(True)

        self._timer = QTimer(self)

        # animation
        fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(fade_effect)

        self._animation = QPropertyAnimation(fade_effect, b"opacity")
        self._animation.setDuration(200)
        self._animation.setStartValue(0)
        self._animation.setEndValue(self._opacity)

        # toast background
        layout = QHBoxLayout()
        layout.addWidget(self._label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet("QWidget { background: #444444; border-radius: 5px; }")
        self._setNotificationSizeBasedOnTextSize()
        self.setLayout(layout)

    def show_notification(self):
        if self._timer.isActive():
            pass
        else:
            self._animation.setDirection(QAbstractAnimation.Direction.Forward)
            self._animation.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
            if self._duration is not None:
                self._timer.singleShot(self._duration, self._hide_notification)
        return self.show()

    def close_notification(self):
        self._animation.setStartValue(self._opacity)
        self._animation.setEndValue(0)
        self._animation.finished.connect(self.deleteLater)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _hide_notification(self):
        self._timer.stop()
        self._animation.finished.connect(self.close)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def setPosition(self, pos):
        geo = self.geometry()
        geo.moveCenter(pos)
        self.setGeometry(geo)

    def setAlignment(self, alignment: Qt.AlignmentFlag):
        self._label.setAlignment(alignment)

    def setFont(self, font: QFont):
        self._label.setFont(font)
        self._setNotificationSizeBasedOnTextSize()

    def _setNotificationSizeBasedOnTextSize(self):
        self.setFixedWidth(self._label.sizeHint().width() * 2)
        self.setFixedHeight(self._label.sizeHint().height() * 2)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if e.type() == 14:  # resize event
            self.setPosition(QPoint(self._parent.rect().center().x(), self._parent.rect().center().y()))
        elif isinstance(obj, Notification):
            if e.type() == 75:  # polish event
                self._label.setStyleSheet(f"QLabel#popupLbl {{ color: {self._foregroundColor}; padding: 5px; }}")
                self.setStyleSheet(f"QWidget {{ background-color: {self._backgroundColor}; border-radius: 5px; }}")
        return super().eventFilter(obj, e)
