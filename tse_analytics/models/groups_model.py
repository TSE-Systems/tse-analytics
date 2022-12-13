from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_datatools.data.group import Group


class GroupsModel(QAbstractTableModel):

    header = ("Name", "Animals in group")

    def __init__(self, items: list[Group], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        item = self.items[index.row()]
        values = (item.name, len(item.animal_ids))
        return values[index.column()]

    def headerData(self, col: int, orientation: int, role: int):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
