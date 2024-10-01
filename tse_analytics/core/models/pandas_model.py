import numpy as np
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.manager import Manager


class PandasModel(QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    color = QColor("#f4a582")

    def __init__(self, df: pd.DataFrame, calculate=False, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.calulate = calculate
        self._data = np.array(df.values)
        self._cols = df.columns
        self.row_count, self.column_count = np.shape(self._data)

        if calculate:
            self.q1 = df.quantile(0.25, numeric_only=True)
            self.q3 = df.quantile(0.75, numeric_only=True)

    def rowCount(self, parent=None):
        return self.row_count

    def columnCount(self, parent=None):
        return self.column_count

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row(), index.column()])
        if self.calulate and role == Qt.ItemDataRole.BackgroundRole:
            if Manager.data.outliers_params.mode == OutliersMode.HIGHLIGHT:
                value = self._data[index.row(), index.column()]
                if isinstance(value, int | float):
                    var_name = str(self._cols[index.column()])
                    if (
                        var_name in Manager.data.selected_dataset.variables
                        and Manager.data.selected_dataset.variables[var_name].remove_outliers
                    ):
                        q1 = self.q1[var_name]
                        q3 = self.q3[var_name]
                        iqr = q3 - q1
                        coef = Manager.data.outliers_params.coefficient
                        if (value < (q1 - coef * iqr)) or (value > (q3 + coef * iqr)):
                            return PandasModel.color
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._cols[section]
            elif orientation == Qt.Orientation.Vertical:
                return section
        return None
