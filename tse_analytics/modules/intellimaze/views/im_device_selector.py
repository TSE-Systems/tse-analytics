from PySide6.QtWidgets import QAbstractItemView, QWidget, QListWidget


class IMDeviceSelector(QListWidget):
    def __init__(self, device_ids: list[str], callback, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.addItems(device_ids)
        self.callback = callback
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        selected_devices = [item.text() for item in self.selectedItems()]
        self.callback(selected_devices)
