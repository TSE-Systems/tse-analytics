"""Configuration table for the Composite Performance Score widget.

Lists every numeric variable of a datatable with per-variable controls: an
*Include* checkbox, a *Direction* combo (higher-is-better / lower-is-better) and
a *Weight* spin box.  ``VariablesTableWidget`` only supports row selection, so a
dedicated table is needed to host the editable per-row cells.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils.ui import set_inactive_palette

_DIRECTION_HIGHER = "Higher is better"
_DIRECTION_LOWER = "Lower is better"


class ScoreConfigTableWidget(QTableWidget):
    """Per-variable include/direction/weight configuration table."""

    _COLUMNS = ["Variable", "Include", "Direction", "Weight"]

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # Sorting would desync the cell widgets from their items, so keep it off.
        self.setSortingEnabled(False)
        self.setColumnCount(len(self._COLUMNS))
        self.setHorizontalHeaderLabels(self._COLUMNS)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setMinimumSectionSize(20)
        self.verticalHeader().setDefaultSectionSize(20)
        self.setMaximumHeight(600)
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

        set_inactive_palette(self)

        # Keep per-row widgets around for state extraction.
        self._checkboxes: dict[str, QCheckBox] = {}
        self._direction_combos: dict[str, QComboBox] = {}
        self._weight_spinboxes: dict[str, QDoubleSpinBox] = {}
        self._row_order: list[str] = []

    def set_data(
        self,
        variables: dict[str, Variable],
        selected_variables: list[str],
        directions: dict[str, str],
        weights: dict[str, float],
    ) -> None:
        """Build one row per variable, restoring state from the saved settings."""
        self._checkboxes.clear()
        self._direction_combos.clear()
        self._weight_spinboxes.clear()
        self._row_order = list(variables.keys())

        self.setRowCount(len(variables))
        for row, variable in enumerate(variables.values()):
            name = variable.name

            name_item = QTableWidgetItem(name)
            tooltip = " — ".join(part for part in (variable.unit, variable.description) if part)
            if tooltip:
                name_item.setToolTip(tooltip)
            self.setItem(row, 0, name_item)

            checkbox = QCheckBox()
            checkbox.setChecked(name in selected_variables)
            self.setCellWidget(row, 1, _center(checkbox))
            self._checkboxes[name] = checkbox

            combo = QComboBox()
            combo.addItems([_DIRECTION_HIGHER, _DIRECTION_LOWER])
            combo.setCurrentText(_DIRECTION_LOWER if directions.get(name) == "lower" else _DIRECTION_HIGHER)
            self.setCellWidget(row, 2, combo)
            self._direction_combos[name] = combo

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0.0, 100.0)
            spinbox.setSingleStep(0.5)
            spinbox.setDecimals(2)
            spinbox.setValue(float(weights.get(name, 1.0)))
            self.setCellWidget(row, 3, spinbox)
            self._weight_spinboxes[name] = spinbox

        self.resizeColumnsToContents()

    def get_config(self) -> tuple[list[str], dict[str, str], dict[str, float]]:
        """Return ``(included_names, directions, weights)`` in table order.

        ``directions`` maps name -> ``"higher"`` | ``"lower"``; ``weights`` maps
        name -> float.  Both cover every row so the settings round-trip fully.
        """
        included: list[str] = []
        directions: dict[str, str] = {}
        weights: dict[str, float] = {}
        for name in self._row_order:
            if self._checkboxes[name].isChecked():
                included.append(name)
            directions[name] = "lower" if self._direction_combos[name].currentText() == _DIRECTION_LOWER else "higher"
            weights[name] = self._weight_spinboxes[name].value()
        return included, directions, weights


def _center(widget: QWidget) -> QWidget:
    """Wrap a widget in a container that centers it within a table cell."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return container
