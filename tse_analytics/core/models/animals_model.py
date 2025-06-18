from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset


class AnimalsModel(QAbstractTableModel):
    """
    A table model for displaying and managing animal data from a dataset.

    This model provides a tabular representation of animals with their properties,
    allowing for display, editing, and toggling of animal visibility.
    """
    def __init__(self, dataset: Dataset, parent=None):
        """
        Initialize the animals model with the given dataset.

        Args:
            dataset (Dataset): The dataset containing animal information.
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)

        self.dataset = dataset
        self.items = list(dataset.animals.values())

        self.header = ["Animal"]
        if len(self.items) > 0:
            properties_header = list(self.items[0].properties.keys())
            self.header = self.header + properties_header

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        """
        Return the data stored at the given index for the specified role.

        Args:
            index (QModelIndex): The index of the requested data.
            role (Qt.ItemDataRole): The role for which to return the data.

        Returns:
            Various: The requested data. Type depends on the role and column.
            - For column 0:
                - DisplayRole/EditRole: Returns the animal ID (str)
                - DecorationRole: Returns the animal color (QColor)
                - CheckStateRole: Returns the enabled state (Qt.CheckState)
            - For other columns:
                - DisplayRole/EditRole: Returns the property value
        """
        item = self.items[index.row()]
        match index.column():
            case 0:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                    return item.id
                elif role == Qt.ItemDataRole.DecorationRole:
                    return QColor(item.color)
                elif role == Qt.ItemDataRole.CheckStateRole:
                    return Qt.CheckState.Checked if item.enabled else Qt.CheckState.Unchecked
            case _:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                    return item.properties[self.header[index.column()]]

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole = ...):
        """
        Set the data for the item at index to value for the given role.

        Args:
            index (QModelIndex): The index of the item to modify.
            value: The new value to set.
            role (Qt.ItemDataRole): The role for which to set the data.

        Returns:
            bool: True if the data was successfully set, False otherwise.

        Note:
            - For column 0:
                - CheckStateRole: Updates the animal's enabled state
                - EditRole: Renames the animal ID
            - For other columns:
                - EditRole: Updates the corresponding property value
        """
        item = self.items[index.row()]
        col = index.column()
        match col:
            case 0:
                if role == Qt.ItemDataRole.CheckStateRole:
                    item.enabled = value == Qt.CheckState.Checked.value
                    messaging.broadcast(messaging.DataChangedMessage(self, self.dataset))
                    return True
                elif role == Qt.ItemDataRole.EditRole:
                    old_id = item.id
                    item.id = value
                    self.dataset.rename_animal(old_id, item)
                    return True
            case _:
                if role == Qt.ItemDataRole.EditRole:
                    item.properties[self.header[col]] = value
                    return True

    def flags(self, index: QModelIndex):
        """
        Return the item flags for the given index.

        Args:
            index (QModelIndex): The index for which to return the flags.

        Returns:
            Qt.ItemFlag: The flags for the item at the given index.
            - For column 0: Selectable, Enabled, UserCheckable, and Editable
            - For other columns: Selectable, Enabled, and Editable
        """
        match index.column():
            case 0:
                return (
                    Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsEnabled
                    | Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsEditable
                )
            case _:
                return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

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
            int: The number of animals in the dataset.
        """
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        """
        Return the number of columns in the model.

        Args:
            parent (QModelIndex): The parent index (unused in table models).

        Returns:
            int: The number of columns (animal ID + properties).
        """
        return len(self.header)
