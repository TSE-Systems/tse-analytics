from dataclasses import dataclass

import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_save_file_name
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.transitions.processor import (
    IntelliCageTransitionsResult,
    get_intellicage_transitions_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase

_INVALID_SHEET_CHARS = str.maketrans("[]:*?/\\", "_______")


def _sanitize_sheet_name(name: str) -> str:
    """Make a string usable as an Excel sheet name (invalid chars replaced, max 31 chars)."""
    return name.translate(_INVALID_SHEET_CHARS)[:31]


@dataclass
class TransitionsWidgetSettings:
    alpha: float = 0.05
    include_diagonal: bool = True


@toolbox_plugin(
    category="IntelliCage",
    label="Transitions",
    icon=":/icons/icons8-transition-both-directions-16.png",
    order=0,
    dataset_types=("IntelliCage", "IntelliMaze"),
    required_datatable_name="Visits",
)
class TransitionsWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            TransitionsWidgetSettings,
            "Transitions",
            parent,
        )

        self.matrices: dict[str, dict[str, pd.DataFrame]] | None = None

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        toolbar.addWidget(QLabel("Alpha:"))
        self.alpha_spinbox = QDoubleSpinBox(toolbar)
        self.alpha_spinbox.setRange(0.001, 0.5)
        self.alpha_spinbox.setSingleStep(0.005)
        self.alpha_spinbox.setDecimals(3)
        self.alpha_spinbox.setValue(self._settings.alpha)
        toolbar.addWidget(self.alpha_spinbox)
        toolbar.addSeparator()

        self.include_diagonal_checkbox = QCheckBox("Include self-transitions", toolbar)
        self.include_diagonal_checkbox.setChecked(self._settings.include_diagonal)
        toolbar.addWidget(self.include_diagonal_checkbox)
        toolbar.addSeparator()

        self.export_excel_action = toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export to Excel")
        self.export_excel_action.triggered.connect(self._export_to_excel)
        self.export_excel_action.setEnabled(False)

    def _get_settings_value(self):
        return TransitionsWidgetSettings(
            self.alpha_spinbox.value(),
            self.include_diagonal_checkbox.isChecked(),
        )

    def _update(self):
        self.report_view.clear()
        self.matrices = None

        if "Corner" not in self.datatable.df.columns:
            make_toast(
                self,
                self.title,
                "This datatable has no 'Corner' column. Open the IntelliCage Visits datatable.",
                duration=4000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        settings = self._get_settings_value()

        columns = ["Timedelta", "Animal", "Corner"]
        df = self.datatable.get_filtered_df(columns)
        df = df.dropna(subset=["Animal", "Corner"])

        if df.empty:
            make_toast(
                self,
                self.title,
                "No data to analyze.",
                duration=2000,
                preset=ToastPreset.WARNING,
            ).show()
            return

        self.update_action.setEnabled(False)
        self.export_excel_action.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(
            get_intellicage_transitions_result,
            df,
            settings.alpha,
            settings.include_diagonal,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: IntelliCageTransitionsResult):
        self.report_view.set_content(result.report)
        self.matrices = result.matrices

    def _on_error(self, error):
        make_toast(
            self,
            self.title,
            "Analysis failed. See the log for details.",
            duration=4000,
            preset=ToastPreset.ERROR,
        ).show()

    def _finished(self):
        self.toast.hide()
        self.update_action.setEnabled(True)
        self.export_excel_action.setEnabled(bool(self.matrices))

    def _export_to_excel(self) -> None:
        if not self.matrices:
            return
        filename = get_save_file_name(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if not filename:
            return

        used: set[str] = set()
        with pd.ExcelWriter(filename) as writer:
            for animal_id, animal_matrices in self.matrices.items():
                for name, matrix in animal_matrices.items():
                    sheet_name = _sanitize_sheet_name(f"{animal_id} {name}")
                    suffix = 1
                    while sheet_name in used:
                        tag = f"_{suffix}"
                        sheet_name = _sanitize_sheet_name(f"{animal_id} {name}")[: 31 - len(tag)] + tag
                        suffix += 1
                    used.add(sheet_name)
                    matrix.to_excel(writer, sheet_name=sheet_name)
