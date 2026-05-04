"""Table model for editing the phases of a TIME_PHASES :class:`Factor`.

Mirrors :mod:`tse_analytics.core.models.time_phases_model` but operates on a
factor's own phase list and keeps ``factor.levels`` in sync with the phases.
"""

from datetime import timedelta

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.color_manager import get_factor_level_color_hex
from tse_analytics.core.data.shared import ByElapsedTimeConfig, Factor, FactorLevel, TimePhase


class FactorTimePhasesModel(QAbstractTableModel):
    header = ("Name", "Start timestamp")

    def __init__(self, factor: Factor | None = None, parent=None):
        super().__init__(parent)
        self.factor: Factor | None = None
        self.set_factor(factor)

    def set_factor(self, factor: Factor | None) -> None:
        self.beginResetModel()
        self.factor = factor
        self.endResetModel()

    @property
    def items(self) -> list[TimePhase]:
        if self.factor is None or not isinstance(self.factor.config, ByElapsedTimeConfig):
            return []
        return self.factor.config.phases

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            values = (item.name, str(pd.to_timedelta(item.start_timestamp)))
            return values[index.column()]
        return None

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole = ...):
        if role != Qt.ItemDataRole.EditRole or self.factor is None:
            return False

        item = self.items[index.row()]
        if index.column() == 0:
            new_name = str(value).strip()
            if not new_name or new_name == item.name:
                return False
            # Disallow duplicate phase names.
            if any(p.name == new_name for p in self.items if p is not item):
                return False
            old_name = item.name
            item.name = new_name
            self.factor.levels[old_name].name = new_name
            self.factor.levels[new_name] = self.factor.levels.pop(old_name)
            return True
        if index.column() == 1:
            try:
                item.start_timestamp = pd.to_timedelta(value).to_pytimedelta()
            except ValueError:
                return False
            return True
        return False

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.header)

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def add_phase(self, name: str, start_timestamp: timedelta) -> bool:
        if self.factor is None or not isinstance(self.factor.config, ByElapsedTimeConfig):
            return False
        if any(p.name == name for p in self.items):
            return False
        phase = TimePhase(name=name, start_timestamp=start_timestamp)
        self.factor.config.phases.append(phase)
        self.factor.levels[name] = FactorLevel(name=name, color=get_factor_level_color_hex(len(self.factor.levels)))
        self.layoutChanged.emit()
        return True

    def delete_phase(self, index: QModelIndex) -> None:
        if self.factor is None or not isinstance(self.factor.config, ByElapsedTimeConfig) or not index.isValid():
            return
        phase = self.items[index.row()]
        del self.factor.config.phases[index.row()]
        self.factor.levels.pop(phase.name, None)
        self.layoutChanged.emit()
