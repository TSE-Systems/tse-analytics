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
    ByAnimalConfig,
    ByAnimalPropertyConfig,
    ByColumnConfig,
    ByElapsedTimeConfig,
    ByTimeOfDayConfig,
    Factor,
    FactorLevel,
    FactorRole,
    FactorSource,
)
from tse_analytics.core.models.factor_time_phases_model import FactorTimePhasesModel
from tse_analytics.views.factors.factors_dialog_ui import Ui_FactorsDialog

# Sources the user can create directly via "Add Factor". BY_TIME_OF_DAY is
# excluded because the dataset auto-creates a single LightCycle factor that
# the user can edit but not duplicate.
_USER_CREATABLE_SOURCES: dict[FactorSource, str] = {
    FactorSource.BY_ANIMAL: "Animal-based",
    FactorSource.BY_ANIMAL_PROPERTY: "Animal property",
    FactorSource.BY_ELAPSED_TIME: "Time phases",
    FactorSource.BY_COLUMN: "Column",
}

# Maps every source to the index of its config page in stackedWidgetConfig
# (page order defined in factors_dialog.ui).
_PAGE_INDEX: dict[FactorSource, int] = {
    FactorSource.BY_ANIMAL: 0,
    FactorSource.BY_TIME_OF_DAY: 1,
    FactorSource.BY_ELAPSED_TIME: 2,
    FactorSource.BY_ANIMAL_PROPERTY: 3,
    FactorSource.BY_COLUMN: 4,
}

_STANDARD_DF_COLUMNS = frozenset({"Animal", "DateTime", "Timedelta", "Bin", "Run"})


def _factor_source(factor: Factor) -> FactorSource:
    """Return the FactorSource of a factor, coercing the discriminator string back to enum."""
    source = factor.config.source
    return source if isinstance(source, FactorSource) else FactorSource(source)


class _AddFactorDialog(QDialog):
    """Small dialog asking for a new factor's name and source."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Add Factor")

        self._name_edit = QLineEdit(self)
        self._source_combo = QComboBox(self)
        for source, label in _USER_CREATABLE_SOURCES.items():
            self._source_combo.addItem(label, source)

        form = QFormLayout()
        form.addRow("Name:", self._name_edit)
        form.addRow("Kind:", self._source_combo)

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
    def factor_source(self) -> FactorSource:
        return self._source_combo.currentData()


class FactorsDialog(QDialog, Ui_FactorsDialog):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.dataset = dataset

        animal_property_keys = self._available_animal_property_keys()
        self.comboBoxFields.addItems(animal_property_keys)
        self.comboBoxAnimalProperty.addItems(animal_property_keys)
        self.comboBoxColumn.addItems(self._available_column_names())

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

        self.comboBoxAnimalProperty.currentTextChanged.connect(self._animal_property_changed)
        self.comboBoxColumn.currentTextChanged.connect(self._column_changed)

        self.selected_factor: Factor | None = None
        self.selected_level: FactorLevel | None = None

    def _available_animal_property_keys(self) -> list[str]:
        if not self.dataset.animals:
            return []
        first_animal = next(iter(self.dataset.animals.values()))
        return list(first_animal.properties.keys())

    def _available_column_names(self) -> list[str]:
        if not self.dataset.datatables:
            return []
        first_dt = next(iter(self.dataset.datatables.values()))
        factor_names = {f.name for f in self.dataset.factors.values()}
        return [
            c for c in first_dt.df.columns
            if c not in _STANDARD_DF_COLUMNS and c not in factor_names
        ]

    def add_factor(self):
        dlg = _AddFactorDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        name = dlg.factor_name
        source = dlg.factor_source
        if not name:
            return
        if any(f.name == name for f in self.factors):
            QMessageBox.warning(self, "Add Factor", f"A factor named '{name}' already exists.")
            return

        factor = self._create_factor(name, source)
        self.factors.append(factor)
        self.listWidgetFactors.addItem(name)

    def _create_factor(self, name: str, source: FactorSource) -> Factor:
        if source == FactorSource.BY_ANIMAL:
            return Factor(
                name=name,
                role=FactorRole.BETWEEN_SUBJECT,
                config=ByAnimalConfig(),
            )
        if source == FactorSource.BY_ANIMAL_PROPERTY:
            keys = self._available_animal_property_keys()
            factor = Factor(
                name=name,
                role=FactorRole.BETWEEN_SUBJECT,
                config=ByAnimalPropertyConfig(property_key=keys[0] if keys else ""),
            )
            self._refresh_animal_property_levels(factor)
            return factor
        if source == FactorSource.BY_ELAPSED_TIME:
            return Factor(
                name=name,
                role=FactorRole.WITHIN_SUBJECT,
                config=ByElapsedTimeConfig(),
            )
        if source == FactorSource.BY_COLUMN:
            columns = self._available_column_names()
            # BY_COLUMN can be either role; default to BETWEEN_SUBJECT and let
            # users edit the role explicitly in a future iteration.
            return Factor(
                name=name,
                role=FactorRole.BETWEEN_SUBJECT,
                config=ByColumnConfig(column=columns[0] if columns else ""),
            )
        raise ValueError(f"Unsupported factor source: {source}")

    def delete_factor(self):
        for item in self.listWidgetFactors.selectedItems():
            factor = next((x for x in self.factors if x.name == item.text()), None)
            if factor is not None:
                self.factors.remove(factor)
            self.listWidgetFactors.takeItem(self.listWidgetFactors.row(item))

    def add_level(self):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByAnimalConfig):
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
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByAnimalConfig):
            return
        for item in self.listWidgetLevels.selectedItems():
            level = next((x for x in self.selected_factor.levels if x.name == item.text()), None)
            if level is not None:
                self.selected_factor.levels.remove(level)
            self.listWidgetLevels.takeItem(self.listWidgetLevels.row(item))

    def extract_levels(self):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByAnimalConfig):
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

        if self.selected_factor is None:
            self.pushButtonDeleteFactor.setEnabled(False)
            self.pushButtonAddLevel.setEnabled(False)
            self.pushButtonDeleteLevel.setEnabled(False)
            self.pushButtonExtractLevels.setEnabled(False)
            self.comboBoxFields.setEnabled(False)
            self.stackedWidgetConfig.setCurrentIndex(0)
            self.phases_model.set_factor(None)
            return

        config = self.selected_factor.config
        is_by_animal = isinstance(config, ByAnimalConfig)
        is_by_time_of_day = isinstance(config, ByTimeOfDayConfig)

        # The auto-created LightCycle factor cannot be deleted by the user.
        self.pushButtonDeleteFactor.setDisabled(is_by_time_of_day)
        self.pushButtonAddLevel.setEnabled(is_by_animal)
        self.pushButtonDeleteLevel.setEnabled(False)
        self.pushButtonExtractLevels.setEnabled(is_by_animal)
        self.comboBoxFields.setEnabled(is_by_animal)

        self.stackedWidgetConfig.setCurrentIndex(_PAGE_INDEX[_factor_source(self.selected_factor)])

        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])
        self._sync_config_page(self.selected_factor)

    def _sync_config_page(self, factor: Factor) -> None:
        config = factor.config
        if isinstance(config, ByTimeOfDayConfig):
            self.timeEditLightStart.blockSignals(True)
            self.timeEditDarkStart.blockSignals(True)
            self.timeEditLightStart.setTime(QTime(config.light_cycle_start))
            self.timeEditDarkStart.setTime(QTime(config.dark_cycle_start))
            self.timeEditLightStart.blockSignals(False)
            self.timeEditDarkStart.blockSignals(False)
            self.phases_model.set_factor(None)
        elif isinstance(config, ByElapsedTimeConfig):
            self.phases_model.set_factor(factor)
        elif isinstance(config, ByAnimalPropertyConfig):
            self.comboBoxAnimalProperty.blockSignals(True)
            if config.property_key:
                self.comboBoxAnimalProperty.setCurrentText(config.property_key)
            self.comboBoxAnimalProperty.blockSignals(False)
            self.phases_model.set_factor(None)
        elif isinstance(config, ByColumnConfig):
            self.comboBoxColumn.blockSignals(True)
            if config.column:
                self.comboBoxColumn.setCurrentText(config.column)
            self.comboBoxColumn.blockSignals(False)
            self.phases_model.set_factor(None)
        else:
            self.phases_model.set_factor(None)

    def current_group_text_changed(self, text: str):
        self.listWidgetAnimals.clear()
        if self.selected_factor is None:
            return
        self.selected_level = next((x for x in self.selected_factor.levels if x.name == text), None)

        is_by_animal = isinstance(self.selected_factor.config, ByAnimalConfig)
        self.pushButtonDeleteLevel.setEnabled(is_by_animal and self.selected_level is not None)

        if not is_by_animal or self.selected_level is None:
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
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByTimeOfDayConfig):
            return
        self.selected_factor.config.light_cycle_start = self.timeEditLightStart.time().toPython()

    def _dark_cycle_start_changed(self):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByTimeOfDayConfig):
            return
        self.selected_factor.config.dark_cycle_start = self.timeEditDarkStart.time().toPython()

    def _animal_property_changed(self, text: str):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByAnimalPropertyConfig):
            return
        self.selected_factor.config.property_key = text
        self._refresh_animal_property_levels(self.selected_factor)
        self.listWidgetLevels.clear()
        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])

    def _refresh_animal_property_levels(self, factor: Factor) -> None:
        config = factor.config
        assert isinstance(config, ByAnimalPropertyConfig)
        if not config.property_key:
            factor.levels = []
            return
        levels = self.dataset.extract_levels_from_property(config.property_key)
        factor.levels = list(levels.values())

    def _column_changed(self, text: str):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByColumnConfig):
            return
        self.selected_factor.config.column = text

    def _add_phase(self):
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByElapsedTimeConfig):
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
        if self.selected_factor is None or not isinstance(self.selected_factor.config, ByElapsedTimeConfig):
            return
        indexes = self.tableViewPhases.selectedIndexes()
        if not indexes:
            return
        self.phases_model.delete_phase(indexes[0])
        self.tableViewPhases.clearSelection()

        self.listWidgetLevels.clear()
        self.listWidgetLevels.addItems([level.name for level in self.selected_factor.levels])
