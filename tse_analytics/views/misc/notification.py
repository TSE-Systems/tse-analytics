from PySide6.QtCore import QAbstractAnimation, QEvent, QObject, QPoint, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class Notification(QWidget):
    def __init__(self, text: str, parent: QWidget, duration=None):
        super().__init__(parent)

        self.__parent = parent
        self.__parent.installEventFilter(self)
        self.installEventFilter(self)
        self.__duration = duration
        self.__opacity = 0.8
        self.__foregroundColor = "#EEEEEE"
        self.__backgroundColor = "#444444"

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        # text in toast (toast foreground)
        self.__label = QLabel(text)
        self.__label.setObjectName("popupLbl")
        self.__label.setStyleSheet("QLabel#popupLbl {{ color: #EEEEEE; padding: 5px; }}")

        self.__label.setMinimumWidth(min(200, self.__label.fontMetrics().boundingRect(text).width() * 2))
        self.__label.setMinimumHeight(self.__label.fontMetrics().boundingRect(text).height() * 2)
        self.__label.setWordWrap(True)

        self.__timer = QTimer(self)

        # animation
        fade_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(fade_effect)

        self.__animation = QPropertyAnimation(fade_effect, b"opacity")
        self.__animation.setDuration(200)
        self.__animation.setStartValue(0)
        self.__animation.setEndValue(self.__opacity)

        # toast background
        layout = QHBoxLayout()
        layout.addWidget(self.__label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet("QWidget { background: #444444; border-radius: 5px; }")
        self.__setNotificationSizeBasedOnTextSize()
        self.setLayout(layout)

    def show_notification(self):
        if self.__timer.isActive():
            pass
        else:
            self.__animation.setDirection(QAbstractAnimation.Direction.Forward)
            self.__animation.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
            if self.__duration is not None:
                self.__timer.singleShot(self.__duration, self.__hide_notification)
        return self.show()

    def close_notification(self):
        self.__animation.setStartValue(self.__opacity)
        self.__animation.setEndValue(0)
        self.__animation.finished.connect(self.deleteLater)
        self.__animation.setDirection(QAbstractAnimation.Direction.Backward)
        self.__animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def __hide_notification(self):
        self.__timer.stop()
        self.__animation.finished.connect(self.close)
        self.__animation.setDirection(QAbstractAnimation.Direction.Backward)
        self.__animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def setPosition(self, pos):
        geo = self.geometry()
        geo.moveCenter(pos)
        self.setGeometry(geo)

    def setAlignment(self, alignment: Qt.AlignmentFlag):
        self.__label.setAlignment(alignment)

    def setFont(self, font: QFont):
        self.__label.setFont(font)
        self.__setNotificationSizeBasedOnTextSize()

    def __setNotificationSizeBasedOnTextSize(self):
        self.setFixedWidth(self.__label.sizeHint().width() * 2)
        self.setFixedHeight(self.__label.sizeHint().height() * 2)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if e.type() == 14:  # resize event
            self.setPosition(QPoint(self.__parent.rect().center().x(), self.__parent.rect().center().y()))
        elif isinstance(obj, Notification):
            if e.type() == 75:  # polish event
                self.__label.setStyleSheet(f"QLabel#popupLbl {{ color: {self.__foregroundColor}; padding: 5px; }}")
                self.setStyleSheet(f"QWidget {{ background-color: {self.__backgroundColor}; border-radius: 5px; }}")
        return super().eventFilter(obj, e)
