from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QToolBar, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.data.data_widget import DataWidget
from tse_analytics.views.data.table_view import TableView


class TableViewWidget(DataWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.table_view = TableView(self)

        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.table_view)

    def clear(self):
        self.table_view.clear()

    def assign_data(self):
        df = Manager.data.get_current_df(calculate_error=False)
        self.table_view.set_data(df)

    def clear_selection(self):
        df = Manager.data.selected_dataset.original_df
        self.table_view.set_data(df)

    def _enable_sorting(self, state: bool):
        self.table_view.set_sorting(state)

    def _resize_columns_width(self):
        # Pass the function to execute
        worker = Worker(self.table_view.resize_columns_width)  # Any other args, kwargs are passed to the run function
        # Execute
        Manager.threadpool.start(worker)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        enable_sorting_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Enable Sorting", self)
        enable_sorting_action.triggered.connect(self._enable_sorting)
        enable_sorting_action.setCheckable(True)
        toolbar.addAction(enable_sorting_action)

        resize_columns_width_action = QAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns", self)
        resize_columns_width_action.triggered.connect(self._resize_columns_width)
        toolbar.addAction(resize_columns_width_action)

        return toolbar
