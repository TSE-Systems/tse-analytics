from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar

from tse_analytics.core.workers.worker import Worker
from tse_analytics.core.manager import Manager
from tse_analytics.views.data.table_view import TableView


class TableViewWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.table_view = TableView(self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.table_view)

    def clear(self):
        self.table_view.clear()

    def set_data(self, df: pd.DataFrame):
        self.table_view.set_data(df)

    def clear_selection(self):
        self.table_view.set_data(Manager.data.selected_dataset.original_df)

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
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        enable_sorting_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Enable Sorting", self)
        enable_sorting_action.triggered.connect(self._enable_sorting)
        enable_sorting_action.setCheckable(True)
        toolbar.addAction(enable_sorting_action)

        resize_columns_width_action = QAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns", self)
        resize_columns_width_action.triggered.connect(self._resize_columns_width)
        toolbar.addAction(resize_columns_width_action)

        return toolbar
