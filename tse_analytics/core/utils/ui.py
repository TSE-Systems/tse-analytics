"""Qt/widget utility helpers."""

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QSizePolicy, QToolButton, QWidget, QWidgetAction


def get_widget_tool_button(parent: QWidget, widget: QWidget, text: str, icon: QIcon) -> QToolButton:
    """Create a QToolButton with a widget in its popup menu.

    This function creates a QToolButton that displays the specified text and icon,
    and shows the specified widget when clicked. The widget is added to the button's
    popup menu as a QWidgetAction.

    Args:
        parent: The parent widget for the button and widget action.
        widget: The widget to display in the popup menu.
        text: The text to display on the button.
        icon: The icon to display on the button.

    Returns:
        A configured QToolButton that shows the widget when clicked.
    """
    button = QToolButton(
        parent,
        popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
        toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
    )
    button.setText(text)
    button.setIcon(icon)

    widget_action = QWidgetAction(parent)
    widget_action.setDefaultWidget(widget)
    button.addAction(widget_action)
    return button


def get_h_spacer_widget(parent: QWidget) -> QWidget:
    """Create a horizontal spacer widget for use in layouts.

    This function creates a widget with an expanding horizontal size policy
    and a minimum vertical size policy, which can be used as a spacer in
    horizontal layouts to push other widgets to the sides.

    Args:
        parent: The parent widget for the spacer.

    Returns:
        A QWidget configured as a horizontal spacer.
    """
    widget = QWidget(parent)
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    return widget


def get_figsize_from_widget(widget: QWidget) -> tuple[float, float]:
    # Get the widget size in pixels
    widget_width = widget.width() - 12
    widget_height = widget.height() - 12

    # Get the DPI (dots per inch) of the screen
    dpi = widget.logicalDpiX()  # or logicalDpiY(), usually the same

    # Convert pixels to inches
    fig_width = widget_width / dpi
    fig_height = widget_height / dpi

    return fig_width, fig_height
