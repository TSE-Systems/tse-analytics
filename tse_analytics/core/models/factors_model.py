from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.data.shared import Factor


class FactorsModel(QAbstractTableModel):
    """
    A table model for displaying factors and their levels.

    This model provides a tabular representation of Factor objects with two columns:
    one for the factor name and one for the comma-separated list of level names.
    """

    header = ("Name", "Levels")

    def __init__(self, items: list[Factor], parent=None):
        """
        Initialize the factors model with the given list of factors.

        Args:
            items (list[Factor]): The list of Factor objects to display.
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
            str or None:
                - For column 0: The factor name
                - For column 1: A comma-separated list of level names
                - None for unsupported roles
        """
        item = self.items[index.row()]
        match index.column():
            case 0:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.name
            case 1:
                if role == Qt.ItemDataRole.DisplayRole:
                    level_names = [level.name for level in item.levels]
                    return f"{', '.join(level_names)}"

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
        return None

    def rowCount(self, parent: QModelIndex = ...):
        """
        Return the number of rows in the model.

        Args:
            parent (QModelIndex): The parent index (unused in table models).

        Returns:
            int: The number of factors.
        """
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        """
        Return the number of columns in the model.

        Args:
            parent (QModelIndex): The parent index (unused in table models).

        Returns:
            int: Always 2, for the "Name" and "Levels" columns.
        """
        return len(self.header)
