import pandas as pd
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QFileDialog, QMenu, QToolBar, QToolButton, QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.misc.raw_data_widget.raw_data_widget_ui import Ui_RawDataWidget


class RawDataWidget(QWidget):
    def __init__(
        self,
        title: str,
        data: dict[str, pd.DataFrame],
        device_ids: list,
        filter_column: str,
        filter_column_is_int: bool,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.data = data
        self.filter_column = filter_column
        self.filter_column_is_int = filter_column_is_int

        self.ui = Ui_RawDataWidget()
        self.ui.setupUi(self)

        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        settings = QSettings()
        self.restoreGeometry(settings.value("RawDataWidget/Geometry"))

        # Setup toolbar
        toolbar = QToolBar(
            "Raw Data Toolbar",
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

        self.ui.listWidgetTables.addItems(self.data.keys())
        self.ui.listWidgetTables.itemSelectionChanged.connect(self._table_selection_changed)

        self.ui.listWidgetDevices.addItems(list(map(str, device_ids)))
        self.ui.listWidgetDevices.itemSelectionChanged.connect(self._cages_selection_changed)

        self.ui.listWidgetTables.setCurrentRow(0)

    def _table_selection_changed(self):
        self._set_data()

    def _cages_selection_changed(self):
        self._set_data()

    def _get_filtered_df(self) -> pd.DataFrame:
        selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
        df = self.data[selected_table]
        selected_devices = [
            int(item.text()) if self.filter_column_is_int else item.text()
            for item in self.ui.listWidgetDevices.selectedItems()
        ]
        if len(selected_devices) > 0 and self.filter_column in df.columns:
            df = df[df[self.filter_column].isin(selected_devices)]
        return df

    def _set_data(self):
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

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("RawDataWidget/Geometry", self.saveGeometry())
