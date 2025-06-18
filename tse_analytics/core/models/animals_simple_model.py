from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.dataset import Dataset


class AnimalsSimpleModel(QAbstractTableModel):
    """
    A simplified table model for displaying animal data from a dataset.

    This model provides a read-only tabular representation of animals with their properties.
    Unlike AnimalsModel, this model does not support editing the data.
    """
    def __init__(self, dataset: Dataset, parent=None):
        """
        Initialize the simplified animals model with the given dataset.

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
