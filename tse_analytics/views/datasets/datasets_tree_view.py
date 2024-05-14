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
    QTreeView,
    QWidget,
)

from tse_analytics.core.licensing import LicenseManager
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
from tse_analytics.views.datasets_merge_dialog import DatasetsMergeDialog


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

        self.customContextMenuRequested.connect(self.__open_menu)
        self.selectionModel().selectionChanged.connect(self._treeview_selection_changed)
        self.selectionModel().currentChanged.connect(self._treeview_current_changed)
        self.doubleClicked.connect(self._treeview_double_clicked)

    def __open_menu(self, position):
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
            if len(indexes) == 1:
                action = menu.addAction("Import meal details...")
                action.triggered.connect(partial(self.__import_meal_details, indexes))

                action_actimot = menu.addAction("Import ActiMot details...")
                action_actimot.triggered.connect(partial(self.__import_actimot_details, indexes))

                if not LicenseManager.is_feature_missing("CurveFitting"):
                    action = menu.addAction("Import calo details...")
                    action.triggered.connect(partial(self.__import_calo_details, indexes))

            action = menu.addAction("Adjust time...")
            action.triggered.connect(partial(self.__adjust_dataset_time, indexes))

            action = menu.addAction("Merge datasets...")
            items = self.model().workspace_tree_item.child_items
            checked_datasets_number = 0
            for item in items:
                if item.checked:
                    checked_datasets_number += 1
            if checked_datasets_number < 2:
                action.setEnabled(False)
            else:
                action.triggered.connect(partial(self.__merge_datasets, indexes))

            action = menu.addAction("Remove datasets")
            action.triggered.connect(partial(self.__remove_datasets, indexes))

        menu.exec_(self.viewport().mapToGlobal(position))

    def __merge_datasets(self, indexes: list[QModelIndex]):
        checked_datasets: list[Dataset] = []
        items = self.model().workspace_tree_item.child_items
        for item in items:
            if item.checked:
                checked_datasets.append(item.dataset)

        dlg = DatasetsMergeDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            new_dataset_name = dlg.lineEditName.text()
            single_run = dlg.checkBoxSingleRun.isChecked()
            Manager.merge_datasets(new_dataset_name, checked_datasets, single_run, self)
            # uncheck all datasets
            items = self.model().workspace_tree_item.child_items
            for item in items:
                item.checked = False

    def __import_meal_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import meal details",
            "",
            "Meal Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                selected_dataset_index = indexes[0]
                Manager.import_meal_details(selected_dataset_index, path)

    def __import_actimot_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import ActiMot details",
            "",
            "ActiMot Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                selected_dataset_index = indexes[0]
                Manager.import_actimot_details(selected_dataset_index, path)

    def __import_calo_details(self, indexes: list[QModelIndex]):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import calo details",
            "",
            "Calo Details Files (*.csv)",
        )
        if path:
            if len(indexes) == 1:
                selected_dataset_index = indexes[0]
                Manager.import_calo_details(selected_dataset_index, path)

    def __adjust_dataset_time(self, indexes: list[QModelIndex]):
        delta, ok = QInputDialog.getText(self, "Enter time delta", "Delta", QLineEdit.EchoMode.Normal, "1 d")
        if ok:
            Manager.data.adjust_dataset_time(indexes, delta)

    def __remove_datasets(self, indexes: list[QModelIndex]):
        Manager.remove_dataset(indexes)

    def _treeview_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if current.isValid():
            item = current.model().getItem(current)
            Manager.messenger.broadcast(SelectedTreeNodeChangedMessage(self, item))
            if isinstance(item, DatasetTreeItem):
                Manager.data.set_selected_dataset(item.dataset)

    def _treeview_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        # indexes = selected.indexes()
        pass

    def _treeview_double_clicked(self, index: QModelIndex):
        if index.isValid():
            item = index.model().getItem(index)
            if isinstance(item, CaloDetailsTreeItem):
                dlg = CaloDetailsDialog(item.calo_details, self)
                result = dlg.exec()
                if result == QDialog.DialogCode.Accepted:
                    Manager.data.append_fitting_results(item.calo_details, dlg.fitting_results)
            elif isinstance(item, MealDetailsTreeItem):
                dlg = MealDetailsDialog(item.meal_details, self)
                result = dlg.exec()
                if result == QDialog.DialogCode.Accepted:
                    pass
            elif isinstance(item, ActimotTreeItem):
                dlg = ActimotDialog(item.actimot_details, self)
                # TODO: check other cases!!
                dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dlg.exec()
                del dlg
                # gc.collect()
                if result == QDialog.DialogCode.Accepted:
                    pass

    def minimumSizeHint(self):
        return QSize(200, 40)
