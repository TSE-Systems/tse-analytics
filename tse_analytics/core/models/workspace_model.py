import pickle

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QSettings, Qt, Signal

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.core.models.workspace_tree_item import WorkspaceTreeItem
from tse_analytics.modules.phenomaster.actimot.io.actimot_loader import ActimotLoader
from tse_analytics.modules.phenomaster.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.calo_details.io.calo_details_loader import CaloDetailsLoader
from tse_analytics.modules.phenomaster.calo_details.models.calo_details_tree_item import CaloDetailsTreeItem
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.io.meal_details_loader import MealDetailsLoader
from tse_analytics.modules.phenomaster.meal_details.models.meal_details_tree_item import MealDetailsTreeItem
from tse_analytics.modules.phenomaster.models.dataset_tree_item import DatasetTreeItem


class WorkspaceModel(QAbstractItemModel):
    checked_item_changed = Signal(TreeItem)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspace = Workspace("Workspace")
        self.workspace_tree_item = WorkspaceTreeItem(self.workspace)

    def rowCount(self, index: QModelIndex):
        if index.isValid():
            return index.internalPointer().child_count()
        return self.workspace_tree_item.child_count()

    def addChild(self, node, parent: QModelIndex | None = None):
        if not parent or not parent.isValid():
            parent = self.workspace_tree_item
        else:
            parent = parent.internalPointer()
        parent.add_child(node)

    def removeRow(self, row: int, parent: QModelIndex | None = None):
        if not parent or not parent.isValid():
            # parent is not valid when it is the root node, since the "parent"
            # method returns an empty QModelIndex
            parentNode = self.workspace_tree_item
        else:
            parentNode = parent.internalPointer()  # the node
        return parentNode.remove_child(row)

    def getItem(self, index: QModelIndex):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.workspace_tree_item

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return self.createIndex(p.row(), 0, p)
        return QModelIndex()

    def columnCount(self, index: QModelIndex):
        if index.isValid():
            return index.internalPointer().column_count()
        return self.workspace_tree_item.column_count()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = None):
        if not index.isValid():
            return None

        item = self.getItem(index)

        if role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == 0:
                return item.tooltip

        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                return item.icon

        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 0:
                return item.foreground

        if role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                return Qt.CheckState.Checked if item.checked else Qt.CheckState.Unchecked

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() != 1:
                return item.data(index.column())

        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        item = self.getItem(index)
        if role == Qt.ItemDataRole.CheckStateRole:
            item.checked = not item.checked
            self.checked_item_changed.emit(item)
            return True
        else:
            return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        return item.flags(index.column())

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.workspace_tree_item.column_names[section]

        return None

    def load_workspace(self, path: str):
        self.beginResetModel()
        with open(path, "rb") as file:
            self.workspace = pickle.load(file)
            self.workspace_tree_item = WorkspaceTreeItem(self.workspace)
            for dataset in self.workspace.datasets:
                dataset_tree_item = DatasetTreeItem(dataset)
                self.__add_children_items(dataset, dataset_tree_item)
                self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def save_workspace(self, path: str):
        with open(path, "wb") as file:
            pickle.dump(self.workspace, file)

    def add_dataset(self, dataset: Dataset):
        self.workspace.datasets.append(dataset)
        dataset_tree_item = DatasetTreeItem(dataset)
        self.__add_children_items(dataset, dataset_tree_item)
        self.beginResetModel()
        self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def add_meal_details(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            meal_details = MealDetailsLoader.load(path, dataset_tree_item.dataset, csv_import_settings)
            if meal_details is not None:
                dataset_tree_item.dataset.meal_details = meal_details
                self.beginResetModel()
                dataset_tree_item.clear()
                self.__add_children_items(dataset_tree_item.dataset, dataset_tree_item)
                self.endResetModel()

    def add_actimot_details(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            actimot_details = ActimotLoader.load(path, dataset_tree_item.dataset, csv_import_settings)
            if actimot_details is not None:
                dataset_tree_item.dataset.actimot_details = actimot_details
                self.beginResetModel()
                dataset_tree_item.clear()
                self.__add_children_items(dataset_tree_item.dataset, dataset_tree_item)
                self.endResetModel()

    def add_calo_details(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            calo_details = CaloDetailsLoader.load(path, dataset_tree_item.dataset, csv_import_settings)
            if calo_details is not None:
                dataset_tree_item.dataset.calo_details = calo_details
                self.beginResetModel()
                dataset_tree_item.clear()
                self.__add_children_items(dataset_tree_item.dataset, dataset_tree_item)
                self.endResetModel()

    def remove_dataset(self, indexes: list[QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            row = index.row()
            self.removeRow(row, parent=index.parent())
            self.workspace.datasets.pop(row)
        self.endResetModel()

    def __add_children_items(self, dataset: Dataset, dataset_tree_item: DatasetTreeItem):
        if dataset.meal_details is not None:
            meal_details_tree_item = MealDetailsTreeItem(dataset.meal_details)
            dataset_tree_item.add_child(meal_details_tree_item)

        if dataset.actimot_details is not None:
            actimot_tree_item = ActimotTreeItem(dataset.actimot_details)
            dataset_tree_item.add_child(actimot_tree_item)

        if dataset.calo_details is not None:
            calo_details_tree_item = CaloDetailsTreeItem(dataset.calo_details)
            dataset_tree_item.add_child(calo_details_tree_item)
