from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QInputDialog, QListWidgetItem, QWidget
from tse_datatools.data.factor import Factor
from tse_datatools.data.group import Group

from tse_analytics.core.manager import Manager
from tse_analytics.views.factors_dialog_ui import Ui_FactorsDialog


class FactorsDialog(QDialog, Ui_FactorsDialog):
    """Factors Dialog"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.comboBoxFields.addItems(("text1", "text2", "text3"))

        self.factors: list[Factor] = []

        if Manager.data.selected_dataset is not None:
            self.factors = list(Manager.data.selected_dataset.factors.values()).copy()
            self.listWidgetFactors.addItems([factor.name for factor in self.factors])

        self.pushButtonAddFactor.clicked.connect(self.add_factor)
        self.pushButtonDeleteFactor.clicked.connect(self.delete_factor)

        self.pushButtonAddGroup.clicked.connect(self.add_group)
        self.pushButtonDeleteGroup.clicked.connect(self.delete_group)
        self.pushButtonExtractGroups.clicked.connect(self.extract_groups)

        self.listWidgetFactors.currentTextChanged.connect(self.current_factor_text_changed)
        self.listWidgetGroups.currentTextChanged.connect(self.current_group_text_changed)
        self.listWidgetAnimals.itemChanged.connect(self.animal_item_changed)

        self.selected_factor: Factor | None = None
        self.selected_group: Group | None = None

    def add_factor(self):
        if Manager.data.selected_dataset is not None:
            text, result = QInputDialog.getText(self, "Add Factor", "Please enter unique factor name:")
            if result:
                factor = Factor(name=text)
                self.factors.append(factor)
                self.listWidgetFactors.addItem(text)

    def delete_factor(self):
        for item in self.listWidgetFactors.selectedItems():
            factor = next((x for x in self.factors if x.name == item.text()), None)
            if factor is not None:
                self.factors.remove(factor)
            self.listWidgetFactors.takeItem(self.listWidgetFactors.row(item))

    def add_group(self):
        if self.selected_factor is not None:
            text, result = QInputDialog.getText(self, "Add Group", "Please enter unique group name:")
            if result:
                group = Group(name=text)
                self.selected_factor.groups.append(group)
                self.listWidgetGroups.addItem(text)

    def delete_group(self):
        for item in self.listWidgetGroups.selectedItems():
            group = next((x for x in self.selected_factor.groups if x.name == item.text()), None)
            if group is not None:
                self.selected_factor.groups.remove(group)
            self.listWidgetGroups.takeItem(self.listWidgetGroups.row(item))

    def extract_groups(self):
        selected_field = self.comboBoxFields.currentText()
        if selected_field is not None:
            groups = Manager.data.selected_dataset.extract_groups_from_field(selected_field)
            self.selected_factor.groups = list(groups.values())
            self.listWidgetGroups.clear()
            self.listWidgetGroups.addItems([group.name for group in self.selected_factor.groups])

    def current_factor_text_changed(self, text: str):
        self.listWidgetGroups.clear()
        self.listWidgetAnimals.clear()
        self.selected_factor = next((x for x in self.factors if x.name == text), None)
        self.pushButtonDeleteFactor.setEnabled(self.selected_factor is not None)
        self.pushButtonAddGroup.setEnabled(self.selected_factor is not None)
        self.pushButtonExtractGroups.setEnabled(self.selected_factor is not None)
        self.comboBoxFields.setEnabled(self.selected_factor is not None)
        if self.selected_factor is not None:
            self.listWidgetGroups.addItems([group.name for group in self.selected_factor.groups])

    def current_group_text_changed(self, text: str):
        self.listWidgetAnimals.clear()
        self.selected_group = next((x for x in self.selected_factor.groups if x.name == text), None)
        self.pushButtonDeleteGroup.setEnabled(self.selected_group is not None)
        if self.selected_group is not None:
            for animal in Manager.data.selected_dataset.animals.values():
                item = QListWidgetItem(str(animal.id))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                if animal.id in self.selected_group.animal_ids:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)

                for group in self.selected_factor.groups:
                    if group != self.selected_group:
                        if animal.id in group.animal_ids:
                            item.setFlags(~Qt.ItemFlag.ItemIsEnabled)
                            break

                self.listWidgetAnimals.addItem(item)

    def animal_item_changed(self, item: QListWidgetItem):
        animal_id = next(
            (animal.id for animal in Manager.data.selected_dataset.animals.values() if animal.id == int(item.text())),
            None,
        )
        if animal_id is not None:
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_group.animal_ids.append(animal_id)
            else:
                self.selected_group.animal_ids.remove(animal_id)
