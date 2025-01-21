from PySide6.QtWidgets import QAbstractItemView, QListWidget, QWidget


class DeviceSelector(QListWidget):
    def __init__(self, device_ids: list[str | int], callback, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.addItems(list(map(str, device_ids)))
        self.callback = callback
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        selected_devices = [item.text() for item in self.selectedItems()]
        self.callback(selected_devices)
