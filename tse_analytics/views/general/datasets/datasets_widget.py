from PySide6.QtCore import QModelIndex, QSize, Qt
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMessageBox,
    QToolBar,
    QToolButton,
    QWidget,
    QVBoxLayout,
    QTreeView,
)

from tse_analytics.core import manager, messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.core.utils import CSV_IMPORT_ENABLED
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellicage.views.intellicage_dialog import IntelliCageDialog
from tse_analytics.modules.intellimaze.submodules.animal_gate.views.animal_gate_dialog import AnimalGateDialog
from tse_analytics.modules.intellimaze.submodules.consumption_scale.views.consumption_scale_dialog import (
    ConsumptionScaleDialog,
)
from tse_analytics.modules.intellimaze.submodules.running_wheel.views.running_wheel_dialog import RunningWheelDialog
from tse_analytics.modules.phenomaster.submodules.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_dialog import ActimotDialog
from tse_analytics.modules.phenomaster.submodules.calo.models.calo_tree_item import CaloDataTreeItem
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_dialog import CaloDialog
from tse_analytics.modules.phenomaster.submodules.drinkfeed.models.drinkfeed_tree_item import DrinkFeedTreeItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_dialog import DrinkFeedDialog
from tse_analytics.modules.phenomaster.submodules.trafficage.models.trafficage_tree_item import TraffiCageTreeItem
from tse_analytics.modules.phenomaster.submodules.trafficage.views.trafficage_dialog import TraffiCageDialog
from tse_analytics.views.general.datasets.adjust_dataset_dialog import AdjustDatasetDialog
from tse_analytics.views.general.datasets.datasets_merge_dialog import DatasetsMergeDialog
from tse_analytics.modules.phenomaster.views.import_csv_dialog import ImportCsvDialog
from tse_analytics.views.toolbox.toolbox_button import ToolboxButton


class DatasetsWidget(QWidget):
    def __init__(self, parent, toolbox_button: ToolboxButton):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.toolbox_button = toolbox_button

        toolbar = QToolBar(
            "Datasets Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        if CSV_IMPORT_ENABLED:
            self.import_button = QToolButton(
                popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
                toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
            )
            self.import_button.setText("Import")
            self.import_button.setIcon(QIcon(":/icons/icons8-database-import-16.png"))
            self.import_button.setEnabled(False)

            import_menu = QMenu("Import", self.import_button)
            import_menu.addAction("Import calo data...").triggered.connect(self._import_calo_data)
            import_menu.addAction("Import drink/feed data...").triggered.connect(self._import_drinkfeed_data)
            import_menu.addAction("Import ActiMot data...").triggered.connect(self._import_actimot_data)
            import_menu.addAction("Import TraffiCage data...").triggered.connect(self._import_trafficage_data)
            self.import_button.setMenu(import_menu)

            toolbar.addWidget(self.import_button)

        self.adjust_dataset_action = toolbar.addAction(QIcon(":/icons/icons8-adjust-16.png"), "Adjust")
        self.adjust_dataset_action.setToolTip("Adjust selected dataset")
        self.adjust_dataset_action.setEnabled(False)
        self.adjust_dataset_action.triggered.connect(self._adjust_dataset)

        self.remove_action = toolbar.addAction(QIcon(":/icons/icons8-remove-16.png"), "Remove")
        self.remove_action.setToolTip("Remove selected item")
        self.remove_action.setEnabled(False)
        self.remove_action.triggered.connect(self._remove_item)

        self.clone_dataset_action = toolbar.addAction(QIcon(":/icons/icons8-copy-16.png"), "Clone")
        self.clone_dataset_action.setToolTip("Clone selected dataset")
        self.clone_dataset_action.setEnabled(False)
        self.clone_dataset_action.triggered.connect(self._clone_dataset)

        self.merge_dataset_action = toolbar.addAction(QIcon(":/icons/icons8-merge-files-16.png"), "Merge")
        self.merge_dataset_action.setToolTip("Merge checked datasets")
        self.merge_dataset_action.setEnabled(False)
        self.merge_dataset_action.triggered.connect(self._merge_datasets)

        self.layout.addWidget(toolbar)

        self.treeView = QTreeView(
            self,
            headerHidden=True,
        )

        pal = self.treeView.palette()
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
        self.treeView.setPalette(pal)

        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        workspace_model = manager.get_workspace_model()
        self.treeView.setModel(workspace_model)

        # self.ui.treeView.customContextMenuRequested.connect(self._open_menu)
        self.treeView.selectionModel().currentChanged.connect(self._treeview_current_changed)
        self.treeView.doubleClicked.connect(self._treeview_double_clicked)

        self.layout.addWidget(self.treeView)

        workspace_model.checkedItemChanged.connect(self._checked_item_changed)
        workspace_model.modelReset.connect(self._expand_all)

    def _expand_all(self):
        self.treeView.expandAll()

    def _get_selected_tree_item(self) -> TreeItem | None:
        selected_indexes = self.treeView.selectedIndexes()
        if len(selected_indexes) > 0:
            selected_index = selected_indexes[0]
            if selected_index.isValid():
                item = selected_index.model().getItem(selected_index)
                return item
        return None

    def _merge_datasets(self):
        checked_datasets: list[Dataset] = []
        items = self.treeView.model().workspace_tree_item.child_items
        for item in items:
            if item.checked:
                checked_datasets.append(item.dataset)

        # check variables compatibility
        first_dataset = checked_datasets[0]
        for dataset in checked_datasets:
            if type(dataset) != type(first_dataset):
                QMessageBox.warning(
                    self,
                    "Cannot merge datasets",
                    "Datasets should be of the same type.",
                    QMessageBox.StandardButton.Abort,
                    QMessageBox.StandardButton.Abort,
                )
                return

            for datatable in dataset.datatables.values():
                if datatable.variables != first_dataset.datatables[datatable.name].variables:
                    QMessageBox.warning(
                        self,
                        "Cannot merge datasets",
                        "List of variables should be the same.",
                        QMessageBox.StandardButton.Abort,
                        QMessageBox.StandardButton.Abort,
                    )
                    return

        dialog = DatasetsMergeDialog(checked_datasets, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.merge_dataset_action.setDisabled(True)
            # uncheck all datasets
            items = self.treeView.model().workspace_tree_item.child_items
            for item in items:
                item.checked = False

    def _import_drinkfeed_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import drink/feed data",
            "",
            "CSV Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                manager.import_drinkfeed_data(selected_dataset_index, path)

    def _import_actimot_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import ActiMot data",
            "",
            "CSV Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                manager.import_actimot_data(selected_dataset_index, path)

    def _import_calo_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import calo data",
            "",
            "CSV Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                manager.import_calo_data(selected_dataset_index, path)

    def _import_trafficage_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import TraffiCage data",
            "",
            "CSV Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                indexes = self.treeView.selectedIndexes()
                selected_dataset_index = indexes[0]
                manager.import_trafficage_data(selected_dataset_index, path)

    def _adjust_dataset(self):
        selected_index = self.treeView.selectedIndexes()[0]
        item = selected_index.model().getItem(selected_index)
        dataset = item.dataset
        dialog = AdjustDatasetDialog(dataset, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item.name = dataset.name
            manager.set_selected_dataset(dataset)

    def _remove_item(self):
        tree_item = self._get_selected_tree_item()
        if tree_item is not None:
            if isinstance(tree_item, DatasetTreeItem):
                if (
                    QMessageBox.question(self, "Remove Dataset", "Do you really want to remove dataset?")
                    == QMessageBox.StandardButton.Yes
                ):
                    LayoutManager.delete_dataset_widgets(tree_item.dataset)
                    selected_indexes = self.treeView.selectedIndexes()
                    manager.remove_dataset(selected_indexes, tree_item.dataset)
                    self.toolbox_button.set_state(False)
                    if CSV_IMPORT_ENABLED:
                        self.import_button.setEnabled(False)
                    self.adjust_dataset_action.setEnabled(False)
                    self.remove_action.setEnabled(False)
                    self.clone_dataset_action.setEnabled(False)
                    self.merge_dataset_action.setEnabled(False)
            elif isinstance(tree_item, DatatableTreeItem):
                if (
                    QMessageBox.question(self, "Remove Datatable", "Do you really want to remove datatable?")
                    == QMessageBox.StandardButton.Yes
                ):
                    selected_indexes = self.treeView.selectedIndexes()
                    manager.remove_datatable(selected_indexes, tree_item.datatable)
                    self.toolbox_button.set_state(False)
                    if CSV_IMPORT_ENABLED:
                        self.import_button.setEnabled(False)
                    self.adjust_dataset_action.setEnabled(False)
                    self.remove_action.setEnabled(False)
                    self.clone_dataset_action.setEnabled(False)
                    self.merge_dataset_action.setEnabled(False)

    def _clone_dataset(self):
        tree_item = self._get_selected_tree_item()
        if tree_item is not None and isinstance(tree_item, DatasetTreeItem):
            name, ok = QInputDialog.getText(
                self,
                "Enter new dataset name",
                "Name",
                QLineEdit.EchoMode.Normal,
                f"Clone of {tree_item.dataset.name}",
            )
            if ok:
                manager.clone_dataset(tree_item.dataset, name)

    def _treeview_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if current.isValid():
            item = current.model().getItem(current)
            messaging.broadcast(messaging.SelectedTreeItemChangedMessage(self, item))

            is_dataset_item = isinstance(item, DatasetTreeItem)
            is_datatable_item = isinstance(item, DatatableTreeItem)

            if is_dataset_item:
                manager.set_selected_dataset(item.dataset)
                manager.set_selected_datatable(None)
                self.toolbox_button.set_dataset_menu(item.dataset)
            elif is_datatable_item:
                manager.set_selected_dataset(item.datatable.dataset)
                manager.set_selected_datatable(item.datatable)
                self.toolbox_button.set_dataset_menu(item.datatable.dataset)

            if CSV_IMPORT_ENABLED:
                self.import_button.setEnabled(is_dataset_item)
            self.adjust_dataset_action.setEnabled(is_dataset_item)
            self.remove_action.setEnabled(is_dataset_item or is_datatable_item)
            self.clone_dataset_action.setEnabled(is_dataset_item)

            self.toolbox_button.set_state(is_datatable_item)

    def _treeview_double_clicked(self, index: QModelIndex) -> None:
        if index.isValid():
            item = index.model().getItem(index)
            if isinstance(item, CaloDataTreeItem):
                dialog = CaloDialog(item.calo_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    dataset = item.calo_data.dataset
                    dataset.append_fitting_results(dialog.fitting_results)
            elif isinstance(item, DrinkFeedTreeItem):
                dialog = DrinkFeedDialog(item.drinkfeed_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
            elif isinstance(item, ActimotTreeItem):
                dialog = ActimotDialog(item.actimot_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                del dialog
                if result == QDialog.DialogCode.Accepted:
                    pass
            elif isinstance(item, TraffiCageTreeItem):
                dialog = TraffiCageDialog(item.trafficage_data.dataset, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                del dialog
                if result == QDialog.DialogCode.Accepted:
                    pass
            elif isinstance(item, ExtensionTreeItem):
                match item.name:
                    case "AnimalGate":
                        dialog = AnimalGateDialog(item.extension_data, self)
                    case "RunningWheel":
                        dialog = RunningWheelDialog(item.extension_data, self)
                    case "ConsumptionScale":
                        dialog = ConsumptionScaleDialog(item.extension_data, self)
                    case "IntelliCage raw data":
                        dialog = IntelliCageDialog(item.extension_data.dataset, self)
                    case _:
                        return
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                result = dialog.exec()
                del dialog
                if result == QDialog.DialogCode.Accepted:
                    pass

    def _checked_item_changed(self, item, state: bool):
        if isinstance(item, DatasetTreeItem):
            items = self.treeView.model().workspace_tree_item.child_items
            checked_datasets_number = 0
            for item in items:
                if item.checked:
                    checked_datasets_number += 1
            self.merge_dataset_action.setDisabled(checked_datasets_number < 2)

    def minimumSizeHint(self) -> QSize:
        return QSize(300, 100)
