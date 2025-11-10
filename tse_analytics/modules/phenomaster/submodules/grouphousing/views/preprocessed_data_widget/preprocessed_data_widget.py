import pandas as pd
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QToolButton, QMenu, QFileDialog

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.preprocessed_data_widget.preprocessed_data_widget_ui import (
    Ui_PreprocessedDataWidget,
)


class PreprocessedDataWidget(QWidget):
    def __init__(
        self,
        data: GroupHousingData,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.data = data
        self.preprocessed_data: dict[str, pd.DataFrame] | None = None

        self.ui = Ui_PreprocessedDataWidget()
        self.ui.setupUi(self)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
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

        self.ui.tableLayout.insertWidget(0, toolbar)

        self.ui.listWidgetTables.addItems([
            "All",
            "TraffiCage",
            "DrinkFeed",
        ])
        self.ui.listWidgetTables.itemSelectionChanged.connect(self._table_selection_changed)

        self.ui.listWidgetAnimals.addItems(list(map(str, self.data.animal_ids)))
        self.ui.listWidgetAnimals.itemSelectionChanged.connect(self._animals_selection_changed)

        self.ui.listWidgetTables.setCurrentRow(0)

    def set_preprocessed_data(self, preprocessed_data: dict[str, pd.DataFrame]) -> None:
        self.preprocessed_data = preprocessed_data
        self._set_data()

    def _table_selection_changed(self):
        self._set_data()

    def _animals_selection_changed(self):
        self._set_data()

    def _get_filtered_df(self) -> pd.DataFrame:
        selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
        df = self.preprocessed_data[selected_table]
        selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        if len(selected_animals) > 0:
            df = df[df["Animal"].isin(selected_animals)]
        return df

    def _set_data(self):
        if self.preprocessed_data is None:
            return

        df = self._get_filtered_df()
        model = PandasSimpleModel(df)
        self.ui.tableView.setModel(model)

    def _resize_columns_width(self):
        worker = Worker(self.ui.tableView.resizeColumnsToContents)
        TaskManager.start_task(worker)

    def _export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            df = self._get_filtered_df()
            df.to_csv(filename, sep=";", index=False)

    def _export_excel(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
            df = self._get_filtered_df()
            with pd.ExcelWriter(filename) as writer:
                df.to_excel(writer, sheet_name=selected_table)
