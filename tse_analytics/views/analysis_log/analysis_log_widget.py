"""Read-only viewer for the per-dataset append-only analysis log.

Subscribes to ``DatasetChangedMessage`` and ``AnalysisLogChangedMessage`` and
renders the active dataset's log entries in a table. The toolbar exposes an
"Export as Notebook…" action that writes a runnable `.ipynb` reproducing the
log against the raw source data.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.export.notebook_exporter import export_dataset_as_notebook


class AnalysisLogWidget(QWidget, messaging.MessengerListener):
    _COLUMNS = ("Sequence", "Timestamp", "Kind", "Description")

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.dataset: Dataset | None = None

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)
        messaging.subscribe(self, messaging.AnalysisLogChangedMessage, self._on_log_changed)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar(
            "Analysis Log Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.export_action = toolbar.addAction(
            QIcon(":/icons/icons8-export-16.png"),
            "Export as Notebook…",
        )
        self.export_action.triggered.connect(self._export_notebook)
        self.export_action.setEnabled(False)
        self._layout.addWidget(toolbar)

        self.table = QTableWidget(0, len(self._COLUMNS), self)
        self.table.setHorizontalHeaderLabels(list(self._COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(
            self._COLUMNS.index("Description"), QHeaderView.ResizeMode.Stretch
        )
        self._layout.addWidget(self.table)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage) -> None:
        self.dataset = message.dataset
        self.export_action.setEnabled(self.dataset is not None)
        self._refresh()

    def _on_log_changed(self, message: messaging.AnalysisLogChangedMessage) -> None:
        if self.dataset is None or message.dataset is not self.dataset:
            return
        self._refresh()

    def _refresh(self) -> None:
        self.table.setRowCount(0)
        if self.dataset is None:
            return
        for action in self.dataset.analysis_log:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(action.sequence)))
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(action.timestamp.isoformat(timespec="seconds")),
            )
            self.table.setItem(row, 2, QTableWidgetItem(action.kind))
            self.table.setItem(row, 3, QTableWidgetItem(action.description))

    def _export_notebook(self) -> None:
        if self.dataset is None:
            return
        default_name = f"{self.dataset.name}_reproducibility.ipynb"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export analysis log as notebook",
            default_name,
            "Jupyter Notebook (*.ipynb)",
        )
        if not path:
            return
        try:
            export_dataset_as_notebook(self.dataset, Path(path))
        except Exception as exc:
            logger.exception("Failed to export notebook")
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        QMessageBox.information(self, "Export complete", f"Notebook saved to:\n{path}")
