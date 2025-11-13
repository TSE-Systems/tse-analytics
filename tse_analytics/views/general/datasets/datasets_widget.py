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
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.core.models.workspace_model import WorkspaceModel
from tse_analytics.core.utils import CSV_IMPORT_ENABLED
from tse_analytics.modules.phenomaster.submodules.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.views.actimot_dialog import ActimotDialog
from tse_analytics.modules.phenomaster.submodules.calo.models.calo_tree_item import CaloDataTreeItem
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_dialog import CaloDialog
from tse_analytics.modules.phenomaster.submodules.drinkfeed.models.drinkfeed_tree_item import DrinkFeedTreeItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_dialog import DrinkFeedDialog
from tse_analytics.modules.phenomaster.submodules.grouphousing.models.grouphousing_tree_item import GroupHousingTreeItem
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.grouphousing_dialog import GroupHousingDialog
from tse_analytics.modules.phenomaster.views.import_csv_dialog import ImportCsvDialog
from tse_analytics.toolbox.toolbox_button import ToolboxButton
from tse_analytics.views.general.datasets.adjust_dataset_dialog import AdjustDatasetDialog
from tse_analytics.views.general.datasets.datasets_merge_dialog import DatasetsMergeDialog
from tse_analytics.views.misc.raw_data_widget.raw_data_widget import RawDataWidget
from tse_analytics.toolbox.data_table.data_table_widget import DataTableWidget

"""
Datasets widget module for TSE Analytics.

This module provides a widget for displaying and managing datasets in the application,
including functionality for importing, merging, adjusting, and removing datasets.
The widget displays datasets in a tree view and allows users to interact with them.
"""


class DatasetsWidget(QWidget, messaging.MessengerListener):
    """
    Widget for displaying and managing datasets.

    This widget provides a tree view of datasets and a toolbar with actions for
    importing, merging, adjusting, and removing datasets. It listens for workspace
    changes and updates the tree view accordingly.
    """

    def __init__(self, parent, toolbox_button: ToolboxButton):
        """
        Initialize the DatasetsWidget with parent widget and toolbox button.

        Args:
            parent: Parent widget
            toolbox_button (ToolboxButton): Toolbox button associated with this widget
        """
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

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
            import_menu.addAction("Import group housing data...").triggered.connect(self._import_grouphousing_data)
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

        self._layout.addWidget(toolbar)

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

        self.treeView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.workspace_model = WorkspaceModel(manager.get_workspace())
        self.workspace_model.checkedItemChanged.connect(self._checked_item_changed)
        self.treeView.setModel(self.workspace_model)

        self.treeView.selectionModel().currentChanged.connect(self._treeview_current_changed)
        self.treeView.doubleClicked.connect(self._treeview_double_clicked)

        self._layout.addWidget(self.treeView)

        messaging.subscribe(self, messaging.WorkspaceChangedMessage, self._workspace_changed)

    def _workspace_changed(self, message: messaging.WorkspaceChangedMessage) -> None:
        """
        Handle workspace changed message.

        Updates the workspace model with the new workspace and expands all items in the tree view.

        Args:
            message (messaging.WorkspaceChangedMessage): The workspace changed message
        """
        self.workspace_model.setupModelData(message.workspace)
        self.treeView.expandAll()

    def _get_selected_tree_item(self) -> TreeItem | None:
        """
        Get the currently selected tree item.

        Returns:
            TreeItem | None: The selected tree item, or None if no item is selected
        """
        selected_indexes = self.treeView.selectedIndexes()
        if len(selected_indexes) > 0:
            selected_index = selected_indexes[0]
            if selected_index.isValid():
                item = selected_index.model().getItem(selected_index)
                return item
        return None

    def _merge_datasets(self):
        """
        Merge checked datasets.

        Collects all checked datasets, verifies they are compatible for merging,
        and opens a dialog to configure the merge operation.
        """
        checked_datasets: list[Dataset] = []
        for item in self.workspace_model.root_item.child_items:
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
            for item in self.workspace_model.root_item.child_items:
                item.checked = False

    def _import_drinkfeed_data(self):
        """
        Import drink/feed data from a CSV file.

        Opens a file dialog to select a CSV file, then opens an ImportCsvDialog
        to configure the import. If the dialog is accepted, calls the manager
        to import the drink/feed data.
        """
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
                manager.import_drinkfeed_data(path)

    def _import_actimot_data(self):
        """
        Import ActiMot data from a CSV file.

        Opens a file dialog to select a CSV file, then opens an ImportCsvDialog
        to configure the import. If the dialog is accepted, calls the manager
        to import the ActiMot data.
        """
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
                manager.import_actimot_data(path)

    def _import_calo_data(self):
        """
        Import calo data from a CSV file.

        Opens a file dialog to select a CSV file, then opens an ImportCsvDialog
        to configure the import. If the dialog is accepted, calls the manager
        to import the calo data.
        """
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
                manager.import_calo_data(path)

    def _import_grouphousing_data(self):
        """
        Import group housing data from a CSV file.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import group housing data",
            "",
            "CSV Files (*.csv)",
        )
        if path:
            dialog = ImportCsvDialog(path, self)
            # TODO: check other cases!!
            dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                manager.import_grouphousing_data(path)

    def _adjust_dataset(self):
        """
        Adjust the selected dataset.

        Opens an AdjustDatasetDialog to modify the selected dataset's properties.
        If the dialog is accepted, updates the tree item name and sets the dataset
        as the selected dataset.
        """
        tree_item = self._get_selected_tree_item()
        dataset = tree_item.dataset
        dialog = AdjustDatasetDialog(dataset, self)
        # TODO: check other cases!!
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            tree_item.name = dataset.name
            manager.set_selected_dataset(dataset)

    def _remove_item(self):
        """
        Remove the selected item from the workspace.

        If the selected item is a dataset, prompts for confirmation before removing.
        For other types of items, removes them without confirmation.
        """
        tree_item = self._get_selected_tree_item()
        if tree_item is not None:
            if isinstance(tree_item, DatasetTreeItem):
                if (
                    QMessageBox.question(self, "Remove Dataset", "Do you really want to remove dataset?")
                    == QMessageBox.StandardButton.Yes
                ):
                    LayoutManager.delete_dataset_widgets(tree_item.dataset)
                    manager.remove_dataset(tree_item.dataset)
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
                    manager.remove_datatable(tree_item.datatable)
                    self.toolbox_button.set_state(False)
                    if CSV_IMPORT_ENABLED:
                        self.import_button.setEnabled(False)
                    self.adjust_dataset_action.setEnabled(False)
                    self.remove_action.setEnabled(False)
                    self.clone_dataset_action.setEnabled(False)
                    self.merge_dataset_action.setEnabled(False)

    def _clone_dataset(self):
        """
        Clone the selected dataset.

        Prompts the user for a new dataset name and creates a clone of the
        selected dataset with that name.
        """
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
        """
        Handle selection changes in the tree view.

        Updates the selected dataset and datatable in the manager, enables/disables
        toolbar actions based on the selected item type, and broadcasts a message
        about the selection change.

        Args:
            current (QModelIndex): The currently selected index
            previous (QModelIndex): The previously selected index
        """
        if current.isValid():
            item = current.model().getItem(current)
            messaging.broadcast(messaging.SelectedTreeItemChangedMessage(self, item))

            is_dataset_item = isinstance(item, DatasetTreeItem)
            is_datatable_item = isinstance(item, DatatableTreeItem)

            if is_dataset_item:
                manager.set_selected_dataset(item.dataset)
                manager.set_selected_datatable(None)
                self.toolbox_button.set_enabled_actions(item.dataset, None)
            elif is_datatable_item:
                manager.set_selected_dataset(item.datatable.dataset)
                manager.set_selected_datatable(item.datatable)
                self.toolbox_button.set_enabled_actions(item.datatable.dataset, item.datatable)

            if CSV_IMPORT_ENABLED:
                self.import_button.setEnabled(is_dataset_item)
            self.adjust_dataset_action.setEnabled(is_dataset_item)
            self.remove_action.setEnabled(is_dataset_item or is_datatable_item)
            self.clone_dataset_action.setEnabled(is_dataset_item)

            self.toolbox_button.set_state(is_datatable_item)

    def _treeview_double_clicked(self, index: QModelIndex) -> None:
        """
        Handle double-click events in the tree view.

        Opens appropriate dialogs based on the type of the double-clicked item,
        such as CaloDialog for CaloDataTreeItem, ActimotDialog for ActimotTreeItem, etc.

        Args:
            index (QModelIndex): The index that was double-clicked
        """
        if index.isValid():
            item = index.model().getItem(index)
            if isinstance(item, CaloDataTreeItem):
                dialog = CaloDialog(item.calo_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
            elif isinstance(item, DrinkFeedTreeItem):
                dialog = DrinkFeedDialog(item.drinkfeed_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
            elif isinstance(item, ActimotTreeItem):
                dialog = ActimotDialog(item.actimot_data, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
            elif isinstance(item, GroupHousingTreeItem):
                dialog = GroupHousingDialog(item.grouphousing_data.dataset, self)
                # TODO: check other cases!!
                dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                dialog.show()
            elif isinstance(item, ExtensionTreeItem):
                match item.name:
                    case "IntelliCage raw data":
                        widget = RawDataWidget(
                            item.extension_data.name,
                            item.extension_data.get_raw_data(),
                            item.extension_data.get_device_ids(),
                            "Cage",
                            True,
                            self,
                        )
                    case _:
                        widget = RawDataWidget(
                            item.extension_data.name,
                            item.extension_data.get_raw_data(),
                            item.extension_data.get_device_ids(),
                            "DeviceId",
                            False,
                            self,
                        )
                # TODO: check other cases!!
                widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                widget.show()
            elif isinstance(item, DatatableTreeItem):
                manager.set_selected_dataset(item.datatable.dataset)
                manager.set_selected_datatable(item.datatable)
                self.toolbox_button.set_enabled_actions(item.datatable.dataset, item.datatable)
                widget = DataTableWidget(item.datatable)
                LayoutManager.add_widget_to_central_area(
                    item.datatable.dataset, widget, f"Table - {item.datatable.dataset.name}", QIcon(":/icons/table.png")
                )

    def _checked_item_changed(self, item, state: bool):
        """
        Handle changes to the checked state of tree items.

        Updates the enabled state of the merge datasets action based on the
        number of checked datasets.

        Args:
            item: The tree item whose checked state changed
            state (bool): The new checked state
        """
        if isinstance(item, DatasetTreeItem):
            checked_datasets_number = 0
            for item in self.workspace_model.root_item.child_items:
                if item.checked:
                    checked_datasets_number += 1
            self.merge_dataset_action.setDisabled(checked_datasets_number < 2)

    def minimumSizeHint(self) -> QSize:
        """
        Return the minimum size hint for the widget.

        Returns:
            QSize: The minimum size hint
        """
        return QSize(300, 100)
