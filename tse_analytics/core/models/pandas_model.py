import numpy as np
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode


class PandasModel(QAbstractTableModel):
    """
    A table model for displaying pandas DataFrame data.

    This model provides a tabular representation of a pandas DataFrame,
    with support for highlighting outliers based on the dataset's outlier settings.
    """

    color = QColor("#f4a582")  # Color used for highlighting outliers

    def __init__(self, df: pd.DataFrame, datatable: Datatable, calculate=False, parent=None):
        """
        Initialize the pandas model with the given DataFrame and datatable.

        Args:
            df (pd.DataFrame): The pandas DataFrame to display.
            datatable (Datatable): The datatable associated with this model.
            calculate (bool, optional): Whether to calculate quartiles for outlier detection.
                                       Defaults to False.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        QAbstractTableModel.__init__(self, parent)

        self.datatable = datatable
        self.calculate = calculate
        self._data = np.array(df.values)
        self._cols = df.columns
        self.row_count, self.column_count = np.shape(self._data)

        if calculate:
            self.q1 = df.quantile(0.25, numeric_only=True)
            self.q3 = df.quantile(0.75, numeric_only=True)

    def rowCount(self, parent=None):
        """
        Return the number of rows in the model.

        Args:
            parent: Unused parameter required by the interface.

        Returns:
            int: The number of rows in the DataFrame.
        """
        return self.row_count

    def columnCount(self, parent=None):
        """
        Return the number of columns in the model.

        Args:
            parent: Unused parameter required by the interface.

        Returns:
            int: The number of columns in the DataFrame.
        """
        return self.column_count

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        """
        Return the data stored at the given index for the specified role.

        This method handles both display of data values and highlighting of outliers
        when the outlier detection mode is set to HIGHLIGHT.

        Args:
            index (QModelIndex): The index of the requested data.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            str, QColor, or None:
                - For DisplayRole: The string representation of the data value
                - For BackgroundRole: A color for outliers if applicable
                - None for unsupported roles
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row(), index.column()])
        if self.calculate and role == Qt.ItemDataRole.BackgroundRole:
            if self.datatable.dataset.outliers_settings.mode == OutliersMode.HIGHLIGHT:
                value = self._data[index.row(), index.column()]
                if isinstance(value, int | float):
                    var_name = str(self._cols[index.column()])
                    if var_name in self.datatable.variables and self.datatable.variables[var_name].remove_outliers:
                        q1 = self.q1[var_name]
                        q3 = self.q3[var_name]
                        iqr = q3 - q1
                        coef = self.datatable.dataset.outliers_settings.coefficient
                        if (value < (q1 - coef * iqr)) or (value > (q3 + coef * iqr)):
                            return PandasModel.color
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        """
        Return the header data for the given role, section and orientation.

        Args:
            section (int): The column/row number.
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            str or None:
                - For horizontal orientation: The column name
                - For vertical orientation: The row number
                - None for unsupported roles
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._cols[section]
            elif orientation == Qt.Orientation.Vertical:
                return section
        return None
