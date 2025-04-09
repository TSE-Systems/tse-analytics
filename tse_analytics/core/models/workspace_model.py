import pickle

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QSettings, Qt, Signal

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.core.models.workspace_tree_item import WorkspaceTreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.io.data_loader import import_actimot_data
from tse_analytics.modules.phenomaster.submodules.calo.io.data_loader import import_calo_data
from tse_analytics.modules.phenomaster.submodules.drinkfeed.io.data_loader import import_drinkfeed_data
from tse_analytics.modules.phenomaster.submodules.trafficage.io.data_loader import import_trafficage_data


class WorkspaceModel(QAbstractItemModel):
    checkedItemChanged = Signal(TreeItem, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspace = Workspace("Workspace")
        self.workspace_tree_item = WorkspaceTreeItem(self.workspace)

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

    def parent(self, child: QModelIndex) -> QModelIndex:
        if child.isValid():
            p = child.internalPointer().parent()
            if p:
                return self.createIndex(p.row(), 0, p)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = ...):
        if parent.isValid():
            return parent.internalPointer().child_count()
        return self.workspace_tree_item.child_count()

    def columnCount(self, parent: QModelIndex = ...):
        if parent.isValid():
            return parent.internalPointer().column_count()
        return self.workspace_tree_item.column_count()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = None):
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
        item = self.getItem(index)
        if role == Qt.ItemDataRole.CheckStateRole:
            item.checked = not item.checked
            self.checkedItemChanged.emit(item, item.checked)
            return True
        else:
            return False

    def flags(self, index: QModelIndex):
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
            for dataset in self.workspace.datasets.values():
                dataset_tree_item = DatasetTreeItem(dataset)
                dataset.add_children_tree_items(dataset_tree_item)
                self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def save_workspace(self, path: str):
        with open(path, "wb") as file:
            pickle.dump(self.workspace, file)

    def add_dataset(self, dataset: Dataset):
        self.workspace.datasets[dataset.id] = dataset
        dataset_tree_item = DatasetTreeItem(dataset)
        dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
        self.beginResetModel()
        self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def add_drinkfeed_data(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            drinkfeed_data = import_drinkfeed_data(path, dataset_tree_item.dataset, csv_import_settings)
            if drinkfeed_data is not None:
                dataset_tree_item.dataset.drinkfeed_data = drinkfeed_data
                self.beginResetModel()
                dataset_tree_item.clear()
                dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
                self.endResetModel()

    def add_actimot_data(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            actimot_data = import_actimot_data(path, dataset_tree_item.dataset, csv_import_settings)
            if actimot_data is not None:
                dataset_tree_item.dataset.actimot_data = actimot_data
                self.beginResetModel()
                dataset_tree_item.clear()
                dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
                self.endResetModel()

    def add_calo_data(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            calo_data = import_calo_data(path, dataset_tree_item.dataset, csv_import_settings)
            if calo_data is not None:
                dataset_tree_item.dataset.calo_data = calo_data
                self.beginResetModel()
                dataset_tree_item.clear()
                dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
                self.endResetModel()

    def add_trafficage_data(self, dataset_index: QModelIndex, path: str):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        if dataset_tree_item is not None and dataset_tree_item.dataset is not None:
            settings = QSettings()
            csv_import_settings: CsvImportSettings = settings.value(
                "CsvImportSettings", CsvImportSettings.get_default()
            )
            trafficage_data = import_trafficage_data(path, dataset_tree_item.dataset, csv_import_settings)
            if trafficage_data is not None:
                dataset_tree_item.dataset.trafficage_data = trafficage_data
                self.beginResetModel()
                dataset_tree_item.clear()
                dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
                self.endResetModel()

    def add_datatable(self, datatable: Datatable):
        for child_item in self.workspace_tree_item.child_items:
            if isinstance(child_item, DatasetTreeItem):
                if datatable.dataset == child_item.dataset:
                    self.beginResetModel()
                    child_item.add_child(DatatableTreeItem(datatable))
                    self.endResetModel()
                    return

    def remove_dataset(self, indexes: list[QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            dataset_tree_item: DatasetTreeItem = self.getItem(index)
            row = index.row()
            self.removeRow(row, parent=index.parent())
            self.workspace.datasets.pop(dataset_tree_item.dataset.id)
        self.endResetModel()
