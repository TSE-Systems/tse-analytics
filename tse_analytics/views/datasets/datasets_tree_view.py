from functools import partial

from PySide6.QtCore import QItemSelection, QModelIndex, QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMessageBox,
    QTreeView,
    QWidget,
)

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import SelectedTreeNodeChangedMessage
from tse_analytics.modules.phenomaster.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.actimot.views.actimot_dialog import ActimotDialog
from tse_analytics.modules.phenomaster.calo_details.models.calo_details_tree_item import CaloDetailsTreeItem
from tse_analytics.modules.phenomaster.calo_details.views.calo_details_dialog import CaloDetailsDialog
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.models.meal_details_tree_item import MealDetailsTreeItem
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_dialog import MealDetailsDialog
from tse_analytics.modules.phenomaster.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.views.datasets.datasets_merge_dialog import DatasetsMergeDialog
from tse_analytics.views.import_csv_dialog import ImportCsvDialog


class DatasetsTreeView(QTreeView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        pal = self.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.setPalette(pal)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setModel(Manager.workspace)

        self.customContextMenuRequested.connect(self._open_menu)
        self.selectionModel().selectionChanged.connect(self._treeview_selection_changed)
        self.selectionModel().currentChanged.connect(self._treeview_current_changed)
        # Manager.workspace.checkedItemChanged.connect(self._checked_item_changed)
        self.doubleClicked.connect(self._treeview_double_clicked)

    def _open_menu(self, position):
        indexes = self.selectedIndexes()

        level = None
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu(self)

        if level == 1:
            menu.addAction("Import meal details...").triggered.connect(partial(self._import_meal_details, indexes))

            menu.addAction("Import ActiMot details...").triggered.connect(
                partial(self._import_actimot_details, indexes)
            )

            menu.addAction("Import calo details...").triggered.connect(partial(self._import_calo_details, indexes))

            menu.addSeparator()

            menu.addAction("Adjust time...").triggered.connect(partial(self._adjust_dataset_time, indexes))

            action = menu.addAction("Merge datasets...")
            items = self.model().workspace_tree_item.child_items
            checked_datasets_number = 0
            for item in items:
                if item.checked:
                    checked_datasets_number += 1
            if checked_datasets_number < 2:
                action.setEnabled(False)
            else:
                action.triggered.connect(partial(self._merge_datasets, indexes))

            menu.addAction("Remove dataset").triggered.connect(partial(self._remove_dataset, indexes))
            menu.addAction("Clone dataset...").triggered.connect(partial(self._clone_dataset, indexes))
            menu.addAction("Rename dataset...").triggered.connect(partial(self._rename_dataset, indexes))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _merge_datasets(self, indexes: list[QModelIndex]):
        checked_datasets: list[Dataset] = []
        items = self.model().workspace_tree_item.child_items
        for item in items:
            if item.checked:
                checked_datasets.append(item.dataset)

        # check variables compatibility
        first_variables_set = checked_datasets[0].variables
        for dataset in checked_datasets:
            if dataset.variables != first_variables_set:
                QMessageBox.critical(
                    self,
                    "Cannot merge datasets!",
                    "List of variables should be the same.",
                    buttons=QMessageBox.StandardButton.Abort,
                    defaultButton=QMessageBox.StandardButton.Abort,
                )
                return

        dialog = DatasetsMergeDialog(checked_datasets, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # uncheck all datasets
            items = self.model().workspace_tree_item.child_items
            for item in items:
                item.checked = False

    def _import_meal_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import meal details",
            "",
            "Meal Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                dialog = ImportCsvDialog(path, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_dataset_index = indexes[0]
                    Manager.import_meal_details(selected_dataset_index, path)

    def _import_actimot_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import ActiMot details",
            "",
            "ActiMot Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                dialog = ImportCsvDialog(path, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_dataset_index = indexes[0]
                    Manager.import_actimot_details(selected_dataset_index, path)

    def _import_calo_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import calo details",
            "",
            "Calo Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                dialog = ImportCsvDialog(path, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_dataset_index = indexes[0]
                    Manager.import_calo_details(selected_dataset_index, path)

    def _adjust_dataset_time(self, indexes: list[QModelIndex]):
        delta, ok = QInputDialog.getText(self, "Enter time delta", "Delta", QLineEdit.EchoMode.Normal, "1 d")
        if ok:
            Manager.data.adjust_dataset_time(delta)

    def _remove_dataset(self, indexes: list[QModelIndex]):
        Manager.remove_dataset(indexes)

    def _rename_dataset(self, indexes: list[QModelIndex]):
        selected_index = indexes[0]
        if selected_index.isValid():
            item = selected_index.model().getItem(selected_index)
            name, ok = QInputDialog.getText(
                self, "Enter dataset name", "Name", QLineEdit.EchoMode.Normal, item.dataset.name
            )
            if ok:
                item.rename_dataset(name)

    def _clone_dataset(self, indexes: list[QModelIndex]):
        selected_index = indexes[0]
        if selected_index.isValid():
            item = selected_index.model().getItem(selected_index)
            dataset = item.dataset
            name, ok = QInputDialog.getText(
                self, "Enter new dataset name", "Name", QLineEdit.EchoMode.Normal, f"Clone of {dataset.name}"
            )
            if ok:
                Manager.clone_dataset(dataset, name)

    def _treeview_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if current.isValid():
            item = current.model().getItem(current)
            Manager.messenger.broadcast(SelectedTreeNodeChangedMessage(self, item))
            if isinstance(item, DatasetTreeItem):
                Manager.data.set_selected_dataset(item.dataset)

    def _treeview_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        # indexes = selected.indexes()
        pass

    def _checked_item_changed(self, item, state: bool):
        pass

    def _treeview_double_clicked(self, index: QModelIndex):
        if index.isValid():
            item = index.model().getItem(index)
            if isinstance(item, CaloDetailsTreeItem):
                dialog = CaloDetailsDialog(item.calo_details, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    Manager.data.append_fitting_results(item.calo_details, dialog.fitting_results)
            elif isinstance(item, MealDetailsTreeItem):
                dialog = MealDetailsDialog(item.meal_details, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    pass
            elif isinstance(item, ActimotTreeItem):
                dialog = ActimotDialog(item.actimot_details, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                del dialog
                # gc.collect()
                if result == QDialog.DialogCode.Accepted:
                    pass

    def minimumSizeHint(self):
        return QSize(300, 50)
