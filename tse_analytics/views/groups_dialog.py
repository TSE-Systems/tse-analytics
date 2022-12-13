from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QListWidgetItem, QInputDialog
from tse_datatools.data.group import Group

from tse_analytics.core.manager import Manager
from tse_analytics.views.groups_dialog_ui import Ui_GroupsDialog


class GroupsDialog(QDialog, Ui_GroupsDialog):
    """Groups Dialog"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        self.groups: list[Group] = []
        if Manager.data.selected_dataset is not None:
            self.groups = list(Manager.data.selected_dataset.groups.values()).copy()
            self.listWidgetGroups.addItems([group.name for group in self.groups])

        self.pushButtonAddGroup.clicked.connect(self.add_group)
        self.pushButtonDeleteGroup.clicked.connect(self.delete_group)

        self.listWidgetGroups.currentTextChanged.connect(self.current_group_text_changed)
        self.listWidgetAnimals.itemChanged.connect(self.animal_item_changed)

        self.selected_group: Optional[Group] = None

    def add_group(self):
        if Manager.data.selected_dataset is not None:
            text, result = QInputDialog.getText(self, "Add Group", "Please enter unique group name:")
            if result:
                group = Group(name=text)
                self.groups.append(group)
                self.listWidgetGroups.addItem(text)

    def delete_group(self):
        for item in self.listWidgetGroups.selectedItems():
            group = next((x for x in self.groups if x.name == item.text()), None)
            if group is not None:
                self.groups.remove(group)
            self.listWidgetGroups.takeItem(self.listWidgetGroups.row(item))

    def current_group_text_changed(self, text: str):
        self.listWidgetAnimals.clear()
        self.selected_group = next((x for x in self.groups if x.name == text), None)
        if self.selected_group is not None:
            for animal in Manager.data.selected_dataset.animals.values():
                item = QListWidgetItem(str(animal.id))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                if animal.id in self.selected_group.animal_ids:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

                for group in self.groups:
                    if group != self.selected_group:
                        if animal.id in group.animal_ids:
                            item.setFlags(~Qt.ItemIsEnabled)
                            break

                self.listWidgetAnimals.addItem(item)

    def animal_item_changed(self, item: QListWidgetItem):
        animal_id = next(
            (animal.id for animal in Manager.data.selected_dataset.animals.values() if animal.id == int(item.text())),
            None,
        )
        if animal_id:
            if item.checkState() == Qt.Checked:
                self.selected_group.animal_ids.append(animal_id)
            else:
                self.selected_group.animal_ids.remove(animal_id)
