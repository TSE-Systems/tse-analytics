import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersType


class PandasModel(QAbstractTableModel):
    """
    A table model for displaying pandas DataFrame data.

    This model provides a tabular representation of a pandas DataFrame,
    with support for highlighting outliers based on the dataset's outlier settings.
    """

    outlier_color = QColor("#f4a582")  # Color used for highlighting outliers

    def __init__(
        self,
        df: pd.DataFrame,
        datatable: Datatable,
        parent=None,
    ):
        """
        Initialize the pandas model with the given DataFrame and datatable.

        Args:
            df (pd.DataFrame): The pandas DataFrame to display.
            datatable (Datatable): The datatable associated with this model.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        QAbstractTableModel.__init__(self, parent)

        self.datatable = datatable
        self._df = df
        self.row_count, self.column_count = df.shape

        if self.datatable.outliers_settings.mode == OutliersMode.HIGHLIGHT:
            remove_outliers_for_vars = {
                key: variable for (key, variable) in datatable.variables.items() if variable.remove_outliers
            }
            vars = list(remove_outliers_for_vars)
            if len(remove_outliers_for_vars) > 0:
                match self.datatable.outliers_settings.type:
                    case OutliersType.IQR:
                        self.q1 = self._df[vars].quantile(0.25, numeric_only=True)
                        self.q3 = self._df[vars].quantile(0.75, numeric_only=True)
                    case OutliersType.ZSCORE:
                        self.z_score = ((self._df[vars] - self._df[vars].mean()) / self._df[vars].std()).abs()
                    case OutliersType.THRESHOLDS:
                        pass

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
            return str(self._df.iat[index.row(), index.column()])
        if self.datatable.outliers_settings.mode == OutliersMode.HIGHLIGHT and role == Qt.ItemDataRole.BackgroundRole:
            value = self._df.iat[index.row(), index.column()]
            if isinstance(value, int | float):
                var_name = str(self._df.columns[index.column()])
                if var_name in self.datatable.variables and self.datatable.variables[var_name].remove_outliers:
                    match self.datatable.outliers_settings.type:
                        case OutliersType.IQR:
                            q1 = self.q1[var_name]
                            q3 = self.q3[var_name]
                            iqr = q3 - q1
                            iqr_multiplier = self.datatable.outliers_settings.iqr_multiplier
                            if (value < (q1 - iqr_multiplier * iqr)) or (value > (q3 + iqr_multiplier * iqr)):
                                return PandasModel.outlier_color
                        case OutliersType.ZSCORE:
                            z_score = self.z_score[var_name]
                            if z_score[index.row()] > 3:
                                return PandasModel.outlier_color
                        case OutliersType.THRESHOLDS:
                            if self.datatable.outliers_settings.min_threshold_enabled:
                                if value < self.datatable.outliers_settings.min_threshold:
                                    return PandasModel.outlier_color
                            if self.datatable.outliers_settings.max_threshold_enabled:
                                if value > self.datatable.outliers_settings.max_threshold:
                                    return PandasModel.outlier_color
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            self.datatable.df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

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
                return self._df.columns[section]
            elif orientation == Qt.Orientation.Vertical:
                return section
        return None
