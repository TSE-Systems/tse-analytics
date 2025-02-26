from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox


class CaloDataBoxesModel(QAbstractTableModel):
    header = ["Box", "Ref. Box"]

    def __init__(self, items: list[CaloBox], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            values = (item.box, item.ref_box)
            value = values[index.column()]
            return int(value) if value is not None else None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[section]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.header)
