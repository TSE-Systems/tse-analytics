from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from tse_analytics.data.calo_details_box import CaloDetailsBox


class CaloDetailsBoxesModel(QAbstractTableModel):
    header = ["Box", "Ref. Box"]

    def __init__(self, items: list[CaloDetailsBox], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            values = (item.box, item.ref_box)
            value = values[index.column()]
            return int(value) if value is not None else None

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
