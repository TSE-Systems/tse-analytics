import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMenu, QToolBar, QToolButton, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.report import Report
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.misc.pandas_table_view import PandasTableView


class PandasWidget(QWidget):
    """
    A widget for displaying and interacting with pandas DataFrame data.

    This widget provides a table view of pandas DataFrame data along with a toolbar
    that includes functionality for exporting data to CSV or Excel, resizing columns,
    and adding the data to a report.
    """

    def __init__(self, dataset: Dataset, title: str, parent=None):
        """
        Initialize the PandasWidget.

        Args:
            dataset: The Dataset object associated with this widget.
            title: The title for this widget, used for Excel sheet name and display.
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)

        self.dataset = dataset
        self.title = title
        self.df: pd.DataFrame | None = None

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

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
        export_menu.addAction("Export to CSV...").triggered.connect(self._export_csv)
        export_menu.addAction("Export to Excel...").triggered.connect(self._export_excel)
        self.export_button.setMenu(export_menu)

        toolbar.addWidget(self.export_button)

        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
        )
        # toolbar.addWidget(get_h_spacer_widget(toolbar))
        # toolbar.addAction("Add Report").triggered.connect(self._add_report)

        self._layout.addWidget(toolbar)

        self.pandas_table_view = PandasTableView()
        self._layout.addWidget(self.pandas_table_view)

    def set_data(self, df: pd.DataFrame, resize_columns=True) -> None:
        """
        Set the pandas DataFrame to be displayed in the widget.

        This method updates the internal DataFrame reference and passes the data
        to the table view for display.
        """
        self.df = df
        self.pandas_table_view.set_data(self.df, resize_columns)

    def _export_csv(self):
        """
        Export the current DataFrame to a CSV file.

        This method prompts the user for a file location and saves the DataFrame
        as a CSV file with semicolon separators and no index.
        """
        if self.df is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            self.df.to_csv(filename, sep=";", index=False)

    def _export_excel(self):
        """
        Export the current DataFrame to an Excel file.

        This method prompts the user for a file location and saves the DataFrame
        as an Excel file with the widget's title as the sheet name.
        """
        if self.df is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.df.to_excel(writer, sheet_name=self.title)

    def _resize_columns_width(self):
        """
        Resize the table columns to fit their contents.

        This method uses a worker thread to resize the columns asynchronously,
        preventing the UI from freezing during the operation.
        """
        worker = Worker(
            self.pandas_table_view.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def _add_report(self):
        if self.df is None:
            return
        # self.df.style.set_caption(self.title)

        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.dataset,
                    name,
                    self.df.to_html(),
                )
            )
