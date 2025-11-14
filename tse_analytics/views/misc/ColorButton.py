from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QColorDialog, QPushButton


class ColorButton(QPushButton):
    """
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).
    """

    colorChanged = Signal(object)

    def __init__(self, *args, color=None, **kwargs):
        """
        Initialize the ColorButton widget.

        Args:
            *args: Variable length argument list to pass to QPushButton.
            color: Initial color for the button. If None, no color is set.
            **kwargs: Arbitrary keyword arguments to pass to QPushButton.
        """
        super().__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.setColor(self._default)

    def setColor(self, color):
        """
        Set the current color of the button.

        Args:
            color: The color to set. Can be a string (e.g., '#FF0000') or None to reset.
                  If the color is different from the current one, emits colorChanged signal.
        """
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            self.setStyleSheet(f"background-color: {self._color};")
        else:
            self.setStyleSheet("")

    def color(self):
        """
        Get the current color of the button.

        Returns:
            The current color as a string or None if no color is set.
        """
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.
        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        """
        Handle mouse press events on the button.

        Right-clicking resets the color to the default color.
        Left-clicking is handled by the parent class and triggers onColorPicker via the pressed signal.

        Args:
            e: The mouse event object.
        """
        if e.button() == Qt.MouseButton.RightButton:
            self.setColor(self._default)

        return super().mousePressEvent(e)
