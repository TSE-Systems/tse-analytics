import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class PandasSimpleModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        QAbstractTableModel.__init__(self)

        self._data = df

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None
