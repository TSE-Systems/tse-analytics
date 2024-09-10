import numpy as np
import polars as pl

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.manager import Manager


class PolarsModel(QAbstractTableModel):
    """
    Class to populate a table view with a polars dataframe
    """

    def __init__(self, df: pl.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._data = df.to_numpy()
        self._cols = df.columns
        self.row_count, self.column_count = np.shape(self._data)
        self.q1 = df.quantile(0.25)
        self.q3 = df.quantile(0.75)

    def rowCount(self, parent=None):
        return self.row_count

    def columnCount(self, parent=None):
        return self.column_count

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data[index.row(), index.column()])
            if role == Qt.ItemDataRole.BackgroundRole:
                if Manager.data.outliers_params.mode == OutliersMode.HIGHLIGHT:
                    value = self._data[index.row(), index.column()]
                    if isinstance(value, int | float):
                        var_name = str(self._cols[index.column()])
                        if var_name in self.q1:
                            q1 = self.q1[var_name]
                            q3 = self.q3[var_name]
                            iqr = q3 - q1
                            coef = Manager.data.outliers_params.coefficient
                            if (value < (q1 - coef * iqr)) or (value > (q3 + coef * iqr)):
                                return QColor("#f4a582")
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._cols[section]
            elif orientation == Qt.Orientation.Vertical:
                return section
        return None
