import pandas as pd
from PySide6.QtCore import QModelIndex, Qt, QAbstractListModel


class PandasListModel(QAbstractListModel):
    def __init__(self, df: pd.DataFrame):
        QAbstractListModel.__init__(self)

        self._data = df

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self._data.iloc[index.row()]
            return item[0]

    def rowCount(self, parent=None):
        return self._data.shape[0]
