from functools import partial

from PySide6.QtCore import QSize, Qt, QModelIndex, QItemSelection
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import (
    QToolBar,
    QWidget,
    QAbstractItemView,
    QMenu,
    QMessageBox,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QToolButton,
)

from tse_analytics.core.helper import CSV_IMPORT_ENABLED
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
from tse_analytics.views.datasets.adjust_dataset_dialog import AdjustDatasetDialog
from tse_analytics.views.datasets.datasets_merge_dialog import DatasetsMergeDialog
from tse_analytics.views.datasets.datasets_widget_ui import Ui_DatasetsWidget
from tse_analytics.views.import_csv_dialog import ImportCsvDialog


class DatasetsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_DatasetsWidget()
        self.ui.setupUi(self)

        toolbar = QToolBar("Datasets Toolbar")
        toolbar.setIconSize(QSize(16, 16))

        if CSV_IMPORT_ENABLED:
            self.import_button = QToolButton()
            self.import_button.setText("Import")
            self.import_button.setIcon(QIcon(":/icons/icons8-import-16.png"))
            self.import_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            self.import_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.import_button.setEnabled(False)

            import_menu = QMenu("Import", self.import_button)
            import_menu.addAction("Import calo details...").triggered.connect(self._import_calo_details)
            import_menu.addAction("Import meal details...").triggered.connect(self._import_meal_details)
            import_menu.addAction("Import ActiMot details...").triggered.connect(self._import_actimot_details)
            self.import_button.setMenu(import_menu)

            toolbar.addWidget(self.import_button)

        self.adjust_dataset_action = toolbar.addAction(QIcon(":/icons/icons8-edit-16.png"), "Adjust dataset")
        self.adjust_dataset_action.setEnabled(False)
        self.adjust_dataset_action.triggered.connect(self._adjust_dataset)

        self.layout().insertWidget(0, toolbar)

        pal = self.ui.treeView.palette()
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
        self.ui.treeView.setPalette(pal)

        self.ui.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.treeView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.treeView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.treeView.setModel(Manager.workspace)

        self.ui.treeView.customContextMenuRequested.connect(self._open_menu)
        self.ui.treeView.selectionModel().selectionChanged.connect(self._treeview_selection_changed)
        self.ui.treeView.selectionModel().currentChanged.connect(self._treeview_current_changed)
        # Manager.workspace.checkedItemChanged.connect(self._checked_item_changed)
        self.ui.treeView.doubleClicked.connect(self._treeview_double_clicked)

    def _open_menu(self, position):
        indexes = self.ui.treeView.selectedIndexes()

        level = None
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu(self.ui.treeView)

        if level == 1:
            action = menu.addAction("Merge datasets...")
            items = self.ui.treeView.model().workspace_tree_item.child_items
            checked_datasets_number = 0
            for item in items:
                if item.checked:
                    checked_datasets_number += 1
            if checked_datasets_number < 2:
                action.setEnabled(False)
            else:
                action.triggered.connect(self._merge_datasets)

            menu.addAction("Remove dataset").triggered.connect(partial(self._remove_dataset, indexes))
            menu.addAction("Clone dataset...").triggered.connect(partial(self._clone_dataset, indexes))

        menu.exec_(self.ui.treeView.viewport().mapToGlobal(position))

    def _merge_datasets(self):
        checked_datasets: list[Dataset] = []
        items = self.ui.treeView.model().workspace_tree_item.child_items
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
            items = self.ui.treeView.model().workspace_tree_item.child_items
            for item in items:
                item.checked = False

    def _import_meal_details(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import meal details",
            "",
            "Meal Details Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.ui.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                Manager.import_meal_details(selected_dataset_index, path)

    def _import_actimot_details(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import ActiMot details",
            "",
            "ActiMot Details Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.ui.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                Manager.import_actimot_details(selected_dataset_index, path)

    def _import_calo_details(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import calo details",
            "",
            "Calo Details Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.ui.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                Manager.import_calo_details(selected_dataset_index, path)

    def _adjust_dataset(self):
        selected_index = self.ui.treeView.selectedIndexes()[0]
        item = selected_index.model().getItem(selected_index)
        dataset = item.dataset
        dialog = AdjustDatasetDialog(dataset, dataset.sampling_interval, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item.name = dataset.name
            Manager.data.set_selected_dataset(dataset)

    def _remove_dataset(self, indexes: list[QModelIndex]):
        if (
            QMessageBox.question(self, "Remove Dataset", "Do you really want to remove dataset?")
            == QMessageBox.StandardButton.Yes
        ):
            Manager.remove_dataset(indexes)
            self.import_button.setEnabled(False)
            self.adjust_dataset_action.setEnabled(False)

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
        level = None
        if len(selected) > 0:
            level = 0
            index = selected.indexes()[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        self.adjust_dataset_action.setEnabled(level == 1)
        if CSV_IMPORT_ENABLED:
            self.import_button.setEnabled(level == 1)

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
                if result == QDialog.DialogCode.Accepted:
                    pass

    def minimumSizeHint(self) -> QSize:
        return QSize(300, 100)