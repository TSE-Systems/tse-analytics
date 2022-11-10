from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QDialog, QComboBox
from tse_datatools.data.group import Group

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetChangedMessage
from tse_analytics.views.groups.groups_table_view import GroupsTableView
from tse_analytics.views.groups_dialog import GroupsDialog


class GroupsViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.table_view = GroupsTableView(self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.table_view)

        self.extract_field = "text1"

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)

    def clear(self):
        self.table_view.clear()

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.table_view.set_data(message.data.groups)

    def edit_groups(self):
        dlg = GroupsDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            groups: dict[str, Group] = {}
            for group in dlg.groups:
                groups[group.name] = group
            Manager.data.selected_dataset.set_groups(groups)
            self.table_view.set_data(Manager.data.selected_dataset.groups)
            Manager.messenger.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))

    def extract_groups(self):
        groups = Manager.data.selected_dataset.extract_groups_from_field(field=self.extract_field)
        Manager.data.selected_dataset.set_groups(groups)
        self.table_view.set_data(Manager.data.selected_dataset.groups)
        Manager.messenger.broadcast(DatasetChangedMessage(self, Manager.data.selected_dataset))

    def _field_current_text_changed(self, text: str):
        self.extract_field = text

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        edit_groups_action = QAction(QIcon(":/icons/icons8-edit-16.png"), "Edit Groups", toolbar)
        edit_groups_action.triggered.connect(self.edit_groups)
        toolbar.addAction(edit_groups_action)

        toolbar.addSeparator()

        extract_groups_action = QAction("Extract groups from", toolbar)
        extract_groups_action.triggered.connect(self.extract_groups)
        toolbar.addAction(extract_groups_action)

        field_combo_box = QComboBox()
        field_combo_box.addItems(["text1", "text2", "text3"])
        field_combo_box.setCurrentText("text1")
        field_combo_box.currentTextChanged.connect(self._field_current_text_changed)
        toolbar.addWidget(field_combo_box)

        return toolbar
