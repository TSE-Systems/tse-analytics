import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget, QToolBar, QToolButton, QMenu, QFileDialog

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.misc.pandas_table_view import PandasTableView


class PandasWidget(QWidget):
    def __init__(self, dataset: Dataset, title: str, parent=None):
        super().__init__(parent)

        self.dataset = dataset
        self.title = title
        self.df: pd.DataFrame | None = None

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Setup toolbar
        toolbar = QToolBar(
            "Pandas Widget Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.export_button = QToolButton(
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.export_button.setText("Export")
        self.export_button.setIcon(QIcon(":/icons/icons8-export-16.png"))

        export_menu = QMenu("Export", self.export_button)
        export_menu.addAction("Export to CVS...").triggered.connect(self._export_csv)
        export_menu.addAction("Export to Excel...").triggered.connect(self._export_excel)
        self.export_button.setMenu(export_menu)

        toolbar.addWidget(self.export_button)

        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
        )
        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        self.layout.addWidget(toolbar)

        self.pandas_table_view = PandasTableView()
        self.layout.addWidget(self.pandas_table_view)

    def set_data(self, df: pd.DataFrame) -> None:
        self.df = df
        self.pandas_table_view.set_data(self.df)

    def _export_csv(self):
        if self.df is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            self.df.to_csv(filename, sep=";", index=False)

    def _export_excel(self):
        if self.df is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.df.to_excel(writer, sheet_name=self.title)

    def _resize_columns_width(self):
        worker = Worker(
            self.pandas_table_view.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def _add_report(self):
        if self.df is None:
            return
        # self.df.style.set_caption(self.title)
        self.dataset.report += self.df.to_html()
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
