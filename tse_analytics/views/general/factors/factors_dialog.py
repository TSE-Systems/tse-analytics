from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QInputDialog, QListWidgetItem, QWidget

from tse_analytics.core.color_manager import get_factor_level_color_hex
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Factor, FactorLevel
from tse_analytics.views.general.factors.factors_dialog_ui import Ui_FactorsDialog


class FactorsDialog(QDialog, Ui_FactorsDialog):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.dataset = dataset

        if len(self.dataset.animals) > 0:
            animal_properties = next(iter(self.dataset.animals.values())).properties
            self.comboBoxFields.addItems(list(animal_properties.keys()))

        self.factors = list(self.dataset.factors.values()).copy()
        self.listWidgetFactors.addItems([factor.name for factor in self.factors])

        self.pushButtonAddFactor.clicked.connect(self.add_factor)
        self.pushButtonDeleteFactor.clicked.connect(self.delete_factor)

        self.pushButtonAddLevel.clicked.connect(self.add_level)
        self.pushButtonDeleteLevel.clicked.connect(self.delete_level)
        self.pushButtonExtractLevels.clicked.connect(self.extract_levels)

        self.listWidgetFactors.currentTextChanged.connect(self.current_factor_text_changed)
        self.listWidgetLevels.currentTextChanged.connect(self.current_group_text_changed)
        self.listWidgetAnimals.itemChanged.connect(self.animal_item_changed)

        self.selected_factor: Factor | None = None
        self.selected_level: FactorLevel | None = None

    def add_factor(self):
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

    def add_level(self):
        if self.selected_factor is not None:
            text, result = QInputDialog.getText(self, "Add Level", "Please enter unique level name:")
            if result:
                level = FactorLevel(
                    name=text,
                    color=get_factor_level_color_hex(len(self.selected_factor.levels)),
                )
                self.selected_factor.levels.append(level)
                self.listWidgetLevels.addItem(text)

    def delete_level(self):
        for item in self.listWidgetLevels.selectedItems():
            level = next((x for x in self.selected_factor.levels if x.name == item.text()), None)
            if level is not None:
                self.selected_factor.levels.remove(level)
            self.listWidgetLevels.takeItem(self.listWidgetLevels.row(item))

    def extract_levels(self):
        selected_field = self.comboBoxFields.currentText()
        if selected_field is not None:
            levels = self.dataset.extract_levels_from_property(selected_field)
            self.selected_factor.levels = list(levels.values())
            self.listWidgetLevels.clear()
            self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])

    def current_factor_text_changed(self, text: str):
        self.listWidgetLevels.clear()
        self.listWidgetAnimals.clear()
        self.selected_factor = next((x for x in self.factors if x.name == text), None)
        self.pushButtonDeleteFactor.setEnabled(self.selected_factor is not None)
        self.pushButtonAddLevel.setEnabled(self.selected_factor is not None)
        self.pushButtonExtractLevels.setEnabled(self.selected_factor is not None)
        self.comboBoxFields.setEnabled(self.selected_factor is not None)
        if self.selected_factor is not None:
            self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])

    def current_group_text_changed(self, text: str):
        self.listWidgetAnimals.clear()
        self.selected_level = next((x for x in self.selected_factor.levels if x.name == text), None)
        self.pushButtonDeleteLevel.setEnabled(self.selected_level is not None)
        if self.selected_level is not None:
            animals_ids = list(self.dataset.animals.keys())
            animals_ids.sort()
            for animal_id in animals_ids:
                item = QListWidgetItem(str(animal_id))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                if animal_id in self.selected_level.animal_ids:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)

                for level in self.selected_factor.levels:
                    if level != self.selected_level:
                        if animal_id in level.animal_ids:
                            item.setFlags(~Qt.ItemFlag.ItemIsEnabled)
                            break

                self.listWidgetAnimals.addItem(item)

    def animal_item_changed(self, item: QListWidgetItem):
        animal_id = next(
            (animal.id for animal in self.dataset.animals.values() if animal.id == item.text()),
            None,
        )
        if animal_id is not None:
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_level.animal_ids.append(animal_id)
            else:
                self.selected_level.animal_ids.remove(animal_id)
