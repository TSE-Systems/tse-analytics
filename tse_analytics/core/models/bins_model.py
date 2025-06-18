from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class BinsModel(QAbstractTableModel):
    """
    A table model for displaying bin values.

    This model provides a simple tabular representation of integer bin values
    in a single column.
    """
    header = ["Bin"]

    def __init__(self, items: list[int], parent=None):
        """
        Initialize the bins model with the given list of bin values.

        Args:
            items (list[int]): The list of bin values to display.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        """
        Return the data stored at the given index for the specified role.

        Args:
            index (QModelIndex): The index of the requested data.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            int or None: The bin value as an integer for DisplayRole, None otherwise.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            return int(item)

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        """
        Return the header data for the given role, section and orientation.

        Args:
            col (int): The column/row number.
            orientation (Qt.Orientation): The orientation of the header.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            str or None: The header text for horizontal headers with DisplayRole,
                         None otherwise.
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent: QModelIndex = ...):
        """
        Return the number of rows in the model.

        Args:
            parent (QModelIndex): The parent index (unused in table models).

        Returns:
            int: The number of bin values.
        """
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        """
        Return the number of columns in the model.

        Args:
            parent (QModelIndex): The parent index (unused in table models).

        Returns:
            int: Always 1, as this model only has one column.
        """
        return len(self.header)
