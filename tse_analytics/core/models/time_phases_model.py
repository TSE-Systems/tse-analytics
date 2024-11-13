import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import TimePhase
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class TimePhasesModel(QAbstractTableModel):
    header = ("Name", "Start timestamp")

    def __init__(self, dataset: Dataset, parent=None):
        super().__init__(parent)

        self.dataset = dataset
        self.items = []

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            values = (item.name, str(item.start_timestamp))
            return values[index.column()]

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            if index.column() == 0:
                item.name = value
            elif index.column() == 1:
                try:
                    item.start_timestamp = pd.to_timedelta(value)
                    # Manager.data.selected_dataset.set_time_phases(self.items)
                    messaging.broadcast(messaging.DatasetChangedMessage(self, self.dataset))
                except ValueError:
                    return False
            else:
                return False
            return True

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def add_time_phase(self, time_phase: TimePhase):
        self.items.append(time_phase)
        # Trigger refresh.
        self.layoutChanged.emit()
        # messaging.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))

    def delete_time_phase(self, index):
        # Remove the item and refresh.
        del self.items[index.row()]
        self.layoutChanged.emit()
        # messaging.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))
