from PySide6.QtCore import QAbstractAnimation, QEvent, QObject, QPoint, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class Notification(QWidget):
    """
    A toast-like notification widget that appears temporarily over the parent widget.

    This widget displays a message to the user with a semi-transparent background,
    fades in when shown, and automatically fades out after a specified duration.
    It centers itself in the parent widget and adjusts its position when the parent
    is resized.
    """

    def __init__(self, text: str, parent: QWidget, duration=None):
        """
        Initialize the Notification widget.

        Args:
            text: The message text to display in the notification.
            parent: The parent widget over which the notification will be shown.
            duration: Time in milliseconds before the notification automatically disappears.
                     If None, the notification will remain visible until explicitly closed.
        """
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
        """
        Show the notification with a fade-in animation.

        If a duration was specified during initialization, the notification will
        automatically fade out after that duration. If the notification is already
        visible, this method has no effect.

        Returns:
            The result of the show() method.
        """
        if self._timer.isActive():
            pass
        else:
            self._animation.setDirection(QAbstractAnimation.Direction.Forward)
            self._animation.start(QPropertyAnimation.DeletionPolicy.KeepWhenStopped)
            if self._duration is not None:
                self._timer.singleShot(self._duration, self._hide_notification)
        return self.show()

    def close_notification(self):
        """
        Close the notification with a fade-out animation.

        This method initiates a fade-out animation and deletes the notification
        widget when the animation completes.
        """
        self._animation.setStartValue(self._opacity)
        self._animation.setEndValue(0)
        self._animation.finished.connect(self.deleteLater)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _hide_notification(self):
        """
        Internal method to hide the notification after its duration has elapsed.

        This method stops the timer and initiates a fade-out animation, closing
        the notification when the animation completes.
        """
        self._timer.stop()
        self._animation.finished.connect(self.close)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def setPosition(self, pos):
        """
        Set the position of the notification.

        Args:
            pos: The QPoint representing the center position for the notification.
        """
        geo = self.geometry()
        geo.moveCenter(pos)
        self.setGeometry(geo)

    def setAlignment(self, alignment: Qt.AlignmentFlag):
        """
        Set the text alignment within the notification.

        Args:
            alignment: The Qt alignment flag to use for the text.
        """
        self._label.setAlignment(alignment)

    def setFont(self, font: QFont):
        """
        Set the font for the notification text.

        This method also adjusts the notification size based on the new font.

        Args:
            font: The QFont to use for the notification text.
        """
        self._label.setFont(font)
        self._setNotificationSizeBasedOnTextSize()

    def _setNotificationSizeBasedOnTextSize(self):
        """
        Internal method to adjust the notification size based on the text content.

        This method sets the width and height of the notification to be proportional
        to the size of the text label, ensuring that the notification is large enough
        to display the text comfortably.
        """
        self.setFixedWidth(self._label.sizeHint().width() * 2)
        self.setFixedHeight(self._label.sizeHint().height() * 2)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        """
        Filter events for the notification and its parent widget.

        This method handles:
        - Resize events on the parent widget to keep the notification centered
        - Polish events on the notification to apply styling

        Args:
            obj: The object that received the event.
            e: The event that was received.

        Returns:
            True if the event was handled and should be filtered out, False otherwise.
        """
        if e.type() == 14:  # resize event
            self.setPosition(QPoint(self._parent.rect().center().x(), self._parent.rect().center().y()))
        elif isinstance(obj, Notification):
            if e.type() == 75:  # polish event
                self._label.setStyleSheet(f"QLabel#popupLbl {{ color: {self._foregroundColor}; padding: 5px; }}")
                self.setStyleSheet(f"QWidget {{ background-color: {self._backgroundColor}; border-radius: 5px; }}")
        return super().eventFilter(obj, e)
