from datetime import timedelta

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core.color_manager import get_factor_level_color_hex
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import (
    Factor,
    FactorKind,
    FactorLevel,
    TimePhasesConfig,
)
from tse_analytics.core.models.factor_time_phases_model import FactorTimePhasesModel
from tse_analytics.views.factors.factors_dialog_ui import Ui_FactorsDialog

_KIND_LABELS: dict[FactorKind, str] = {
    FactorKind.ANIMAL: "Animal-based",
    FactorKind.TIME_PHASES: "Time phases",
}

_PAGE_INDEX: dict[FactorKind, int] = {
    FactorKind.ANIMAL: 0,
    FactorKind.LIGHT_CYCLES: 1,
    FactorKind.TIME_PHASES: 2,
}


class _AddFactorDialog(QDialog):
    """Small dialog asking for a new factor's name and kind."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Add Factor")

        self._name_edit = QLineEdit(self)
        self._kind_combo = QComboBox(self)
        for kind, label in _KIND_LABELS.items():
            self._kind_combo.addItem(label, kind)

        form = QFormLayout()
        form.addRow("Name:", self._name_edit)
        form.addRow("Kind:", self._kind_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @property
    def factor_name(self) -> str:
        return self._name_edit.text().strip()

    @property
    def factor_kind(self) -> FactorKind:
        return self._kind_combo.currentData()


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

        self.phases_model = FactorTimePhasesModel(parent=self)
        self.tableViewPhases.setModel(self.phases_model)
        header = self.tableViewPhases.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.pushButtonAddFactor.clicked.connect(self.add_factor)
        self.pushButtonDeleteFactor.clicked.connect(self.delete_factor)

        self.pushButtonAddLevel.clicked.connect(self.add_level)
        self.pushButtonDeleteLevel.clicked.connect(self.delete_level)
        self.pushButtonExtractLevels.clicked.connect(self.extract_levels)

        self.listWidgetFactors.currentTextChanged.connect(self.current_factor_text_changed)
        self.listWidgetLevels.currentTextChanged.connect(self.current_group_text_changed)
        self.listWidgetAnimals.itemChanged.connect(self.animal_item_changed)

        self.timeEditLightStart.editingFinished.connect(self._light_cycle_start_changed)
        self.timeEditDarkStart.editingFinished.connect(self._dark_cycle_start_changed)

        self.toolButtonAddPhase.clicked.connect(self._add_phase)
        self.toolButtonDeletePhase.clicked.connect(self._delete_phase)

        self.selected_factor: Factor | None = None
        self.selected_level: FactorLevel | None = None

    def add_factor(self):
        dlg = _AddFactorDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = dlg.factor_name
        kind = dlg.factor_kind
        if not name:
            return
        if any(f.name == name for f in self.factors):
            QMessageBox.warning(self, "Add Factor", f"A factor named '{name}' already exists.")
            return

        factor = self._create_factor(name, kind)
        self.factors.append(factor)
        self.listWidgetFactors.addItem(name)

    @staticmethod
    def _create_factor(name: str, kind: FactorKind) -> Factor:
        if kind == FactorKind.TIME_PHASES:
            return Factor(
                name=name,
                kind=kind,
                time_phases=TimePhasesConfig(),
            )
        return Factor(name=name, kind=FactorKind.ANIMAL)

    def delete_factor(self):
        for item in self.listWidgetFactors.selectedItems():
            factor = next((x for x in self.factors if x.name == item.text()), None)
            if factor is not None:
                self.factors.remove(factor)
            self.listWidgetFactors.takeItem(self.listWidgetFactors.row(item))

    def add_level(self):
        if self.selected_factor is None or self.selected_factor.kind != FactorKind.ANIMAL:
            return
        text, result = QInputDialog.getText(self, "Add Level", "Please enter unique level name:")
        if result:
            level = FactorLevel(
                name=text,
                color=get_factor_level_color_hex(len(self.selected_factor.levels)),
            )
            self.selected_factor.levels.append(level)
            self.listWidgetLevels.addItem(text)

    def delete_level(self):
        if self.selected_factor is None or self.selected_factor.kind != FactorKind.ANIMAL:
            return
        for item in self.listWidgetLevels.selectedItems():
            level = next((x for x in self.selected_factor.levels if x.name == item.text()), None)
            if level is not None:
                self.selected_factor.levels.remove(level)
            self.listWidgetLevels.takeItem(self.listWidgetLevels.row(item))

    def extract_levels(self):
        if self.selected_factor is None or self.selected_factor.kind != FactorKind.ANIMAL:
            return
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
        self.selected_level = None

        is_factor_selected = self.selected_factor is not None
        kind = self.selected_factor.kind if is_factor_selected else FactorKind.ANIMAL
        is_animal_kind = is_factor_selected and kind == FactorKind.ANIMAL

        self.pushButtonDeleteFactor.setDisabled(is_factor_selected and kind == FactorKind.LIGHT_CYCLES)
        self.pushButtonAddLevel.setEnabled(is_animal_kind)
        self.pushButtonDeleteLevel.setEnabled(False)
        self.pushButtonExtractLevels.setEnabled(is_animal_kind)
        self.comboBoxFields.setEnabled(is_animal_kind)

        self.stackedWidgetConfig.setCurrentIndex(_PAGE_INDEX[kind])

        if not is_factor_selected:
            self.phases_model.set_factor(None)
            return

        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])
        self._sync_config_page(self.selected_factor)

    def _sync_config_page(self, factor: Factor) -> None:
        if factor.kind == FactorKind.LIGHT_CYCLES and factor.light_cycles is not None:
            self.timeEditLightStart.blockSignals(True)
            self.timeEditDarkStart.blockSignals(True)
            self.timeEditLightStart.setTime(QTime(factor.light_cycles.light_cycle_start))
            self.timeEditDarkStart.setTime(QTime(factor.light_cycles.dark_cycle_start))
            self.timeEditLightStart.blockSignals(False)
            self.timeEditDarkStart.blockSignals(False)
        elif factor.kind == FactorKind.TIME_PHASES:
            self.phases_model.set_factor(factor)
        else:
            self.phases_model.set_factor(None)

    def current_group_text_changed(self, text: str):
        self.listWidgetAnimals.clear()
        if self.selected_factor is None:
            return
        self.selected_level = next((x for x in self.selected_factor.levels if x.name == text), None)

        is_animal_kind = self.selected_factor.kind == FactorKind.ANIMAL
        self.pushButtonDeleteLevel.setEnabled(is_animal_kind and self.selected_level is not None)

        if not is_animal_kind or self.selected_level is None:
            return

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
        if self.selected_level is None:
            return
        animal_id = next(
            (animal.id for animal in self.dataset.animals.values() if animal.id == item.text()),
            None,
        )
        if animal_id is not None:
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_level.animal_ids.append(animal_id)
            else:
                self.selected_level.animal_ids.remove(animal_id)

    def _light_cycle_start_changed(self):
        if self.selected_factor is None or self.selected_factor.light_cycles is None:
            return
        self.selected_factor.light_cycles.light_cycle_start = self.timeEditLightStart.time().toPython()

    def _dark_cycle_start_changed(self):
        if self.selected_factor is None or self.selected_factor.light_cycles is None:
            return
        self.selected_factor.light_cycles.dark_cycle_start = self.timeEditDarkStart.time().toPython()

    def _add_phase(self):
        if self.selected_factor is None or self.selected_factor.kind != FactorKind.TIME_PHASES:
            return
        text, result = QInputDialog.getText(self, "Add Phase", "Please enter unique phase name:")
        if not result or not text.strip():
            return
        name = text.strip()

        start_timestamp = timedelta(0)
        if self.phases_model.items:
            start_timestamp = self.phases_model.items[-1].start_timestamp + timedelta(hours=1)

        if not self.phases_model.add_phase(name, start_timestamp):
            QMessageBox.warning(self, "Add Phase", f"A phase named '{name}' already exists.")
            return

        self.listWidgetLevels.clear()
        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])

    def _delete_phase(self):
        if self.selected_factor is None or self.selected_factor.kind != FactorKind.TIME_PHASES:
            return
        indexes = self.tableViewPhases.selectedIndexes()
        if not indexes:
            return
        self.phases_model.delete_phase(indexes[0])
        self.tableViewPhases.clearSelection()

        self.listWidgetLevels.clear()
        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])
