from PySide6.QtWidgets import QAbstractItemView, QListWidget, QWidget


class DeviceSelector(QListWidget):
    """
    A list widget for selecting multiple devices from a list.

    This widget allows users to select one or more devices from a provided list
    and triggers a callback function when the selection changes.
    """

    def __init__(self, device_ids: list[str | int], callback, parent: QWidget | None = None):
        """
        Initialize the DeviceSelector widget.

        Args:
            device_ids: List of device identifiers (strings or integers) to display.
            callback: Function to call when selection changes, receives list of selected device IDs.
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.addItems(list(map(str, device_ids)))
        self.callback = callback
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        """
        Handle selection changes in the device list.

        This method is called automatically when the user changes the selection.
        It collects the IDs of all selected devices and passes them to the callback function.
        """
        selected_devices = [item.text() for item in self.selectedItems()]
        self.callback(selected_devices)
