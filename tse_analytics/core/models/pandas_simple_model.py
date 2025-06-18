import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class PandasSimpleModel(QAbstractTableModel):
    """
    A simplified table model for displaying pandas DataFrame data.

    This model provides a basic tabular representation of a pandas DataFrame
    without additional features like outlier highlighting.
    """
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the simplified pandas model with the given DataFrame.

        Args:
            df (pd.DataFrame): The pandas DataFrame to display.
        """
        QAbstractTableModel.__init__(self)

        self._data = df

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        """
        Return the data stored at the given index for the specified role.

        Args:
            index (QModelIndex): The index of the requested data.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            str or None: The string representation of the data value for DisplayRole,
                        None for unsupported roles.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, parent=None):
        """
        Return the number of rows in the model.

        Args:
            parent: Unused parameter required by the interface.

        Returns:
            int: The number of rows in the DataFrame.
        """
        return self._data.shape[0]

    def columnCount(self, parent=None):
        """
        Return the number of columns in the model.

        Args:
            parent: Unused parameter required by the interface.

        Returns:
            int: The number of columns in the DataFrame.
        """
        return self._data.shape[1]

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
                - For vertical orientation: The row index
                - None for unsupported roles
        """
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None
