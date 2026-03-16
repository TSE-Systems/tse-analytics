from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QMessageBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings, OutliersType
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.models.aggregation_combo_box_delegate import AggregationComboBoxDelegate
from tse_analytics.core.models.variables_model import VariablesModel
from tse_analytics.core.utils import get_widget_tool_button
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values
from tse_analytics.modules.phenomaster.data.variables_helper import cleanup_variables
from tse_analytics.views.variables.add_variable_dialog import AddVariableDialog
from tse_analytics.views.variables.outliers_widget_ui import Ui_OutliersWidget


class VariablesWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.datatable: Datatable | None = None

        messaging.subscribe(self, messaging.DatatableChangedMessage, self._on_datatable_changed)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.outliers_widget = QWidget()
        self.outliers_widget_ui = Ui_OutliersWidget()
        self.outliers_widget_ui.setupUi(self.outliers_widget)
        outliers_button = get_widget_tool_button(
            toolbar,
            self.outliers_widget,
            "Outliers",
            QIcon(":/icons/icons8-electrical-threshold-16.png"),
        )
        toolbar.addWidget(outliers_button)

        self.outliers_widget_ui.radioButtonDetectionOff.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )
        self.outliers_widget_ui.radioButtonHighlightOutliers.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )
        self.outliers_widget_ui.radioButtonRemoveOutliers.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )

        self.outliers_widget_ui.radioButtonIqr.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )
        self.outliers_widget_ui.radioButtonZScore.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )
        self.outliers_widget_ui.radioButtonThresholds.toggled.connect(
            lambda toggled: self._outliers_settings_changed() if toggled else None
        )

        self.outliers_widget_ui.groupBoxMinThreshold.toggled.connect(self._outliers_settings_changed)
        self.outliers_widget_ui.groupBoxMaxThreshold.toggled.connect(self._outliers_settings_changed)
        self.outliers_widget_ui.doubleSpinBoxMinThreshold.valueChanged.connect(self._outliers_settings_changed)
        self.outliers_widget_ui.doubleSpinBoxMaxThreshold.valueChanged.connect(self._outliers_settings_changed)

        self.outliers_widget_ui.doubleSpinBoxIqrMultiplier.valueChanged.connect(self._outliers_settings_changed)

        self.outliers_widget_ui.pushButtonFreezeRemoval.clicked.connect(self._freeze_removal)

        toolbar.addAction("Reset").triggered.connect(self._reset_variables)

        toolbar.addSeparator()
        toolbar.addAction(QIcon(":/icons/icons8-add-16.png"), "Add").triggered.connect(self._add_variable)
        toolbar.addAction(QIcon(":/icons/icons8-remove-16.png"), "Delete").triggered.connect(self._delete_variable)

        self._layout.addWidget(toolbar)

        self.tableView = QTableView(
            self,
            sortingEnabled=True,
        )
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.tableView.setModel(proxy_model)

        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tableView.setItemDelegateForColumn(2, AggregationComboBoxDelegate(self.tableView))

        self._layout.addWidget(self.tableView)

    def _on_datatable_changed(self, message: messaging.DatatableChangedMessage):
        if message.datatable is None:
            self.datatable = None
            self.tableView.model().setSourceModel(None)
            outliers_settings = OutliersSettings()
        else:
            self.datatable = message.datatable
            model = VariablesModel(self.datatable)
            self.tableView.model().setSourceModel(model)
            self.tableView.resizeColumnsToContents()
            outliers_settings = self.datatable.dataset.outliers_settings

        match outliers_settings.mode:
            case OutliersMode.OFF:
                self.outliers_widget_ui.radioButtonDetectionOff.setChecked(True)
            case OutliersMode.HIGHLIGHT:
                self.outliers_widget_ui.radioButtonHighlightOutliers.setChecked(True)
            case OutliersMode.REMOVE:
                self.outliers_widget_ui.radioButtonRemoveOutliers.setChecked(True)

        match outliers_settings.type:
            case OutliersType.IQR:
                self.outliers_widget_ui.radioButtonIqr.setChecked(True)
            case OutliersType.ZSCORE:
                self.outliers_widget_ui.radioButtonZScore.setChecked(True)
            case OutliersType.THRESHOLDS:
                self.outliers_widget_ui.radioButtonThresholds.setChecked(True)

        self.outliers_widget_ui.doubleSpinBoxIqrMultiplier.setValue(outliers_settings.iqr_multiplier)
        self.outliers_widget_ui.groupBoxMinThreshold.setChecked(outliers_settings.min_threshold_enabled)
        self.outliers_widget_ui.doubleSpinBoxMinThreshold.setValue(outliers_settings.min_threshold)
        self.outliers_widget_ui.groupBoxMaxThreshold.setChecked(outliers_settings.max_threshold_enabled)
        self.outliers_widget_ui.doubleSpinBoxMaxThreshold.setValue(outliers_settings.max_threshold)

    def _outliers_settings_changed(self):
        if self.datatable is not None:
            if self.outliers_widget_ui.radioButtonHighlightOutliers.isChecked():
                mode = OutliersMode.HIGHLIGHT
            elif self.outliers_widget_ui.radioButtonRemoveOutliers.isChecked():
                mode = OutliersMode.REMOVE
            else:
                mode = OutliersMode.OFF

            if self.outliers_widget_ui.radioButtonIqr.isChecked():
                type = OutliersType.IQR
            elif self.outliers_widget_ui.radioButtonZScore.isChecked():
                type = OutliersType.ZSCORE
            else:
                type = OutliersType.THRESHOLDS

            outliers_settings = OutliersSettings(
                mode=mode,
                type=type,
                iqr_multiplier=self.outliers_widget_ui.doubleSpinBoxIqrMultiplier.value(),
                min_threshold_enabled=self.outliers_widget_ui.groupBoxMinThreshold.isChecked(),
                min_threshold=self.outliers_widget_ui.doubleSpinBoxMinThreshold.value(),
                max_threshold_enabled=self.outliers_widget_ui.groupBoxMaxThreshold.isChecked(),
                max_threshold=self.outliers_widget_ui.doubleSpinBoxMaxThreshold.value(),
            )
            self.datatable.dataset.apply_outliers(outliers_settings)

    def _reset_variables(self):
        if self.datatable is not None:
            if (
                QMessageBox.question(self, "Reset Variables", "Do you want to reset variables to default state?")
                == QMessageBox.StandardButton.Yes
            ):
                # Close all affected widgets
                LayoutManager.delete_dataset_widgets(self.datatable.dataset)

                # Cleanup old variables
                cleanup_variables(self.datatable.dataset)
                self.datatable.variables = assign_predefined_values(self.datatable.variables)

                model = VariablesModel(self.datatable)
                self.tableView.model().setSourceModel(model)
                self.tableView.resizeColumnsToContents()

    def _add_variable(self) -> None:
        if self.datatable is None:
            return
        dialog = AddVariableDialog(self.datatable, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            model = VariablesModel(self.datatable)
            self.tableView.model().setSourceModel(model)
            self.tableView.resizeColumnsToContents()
        dialog.deleteLater()

    def _delete_variable(self) -> None:
        if self.datatable is None:
            return
        selected_rows = self.tableView.selectionModel().selectedRows()
        if len(selected_rows) > 0:
            if (
                QMessageBox.question(self, "Delete Variables", "Do you want to delete selected variables?")
                == QMessageBox.StandardButton.Yes
            ):
                variable_names = []
                for index in selected_rows:
                    var_name = index.model().data(index.model().index(index.row(), 0))
                    variable_names.append(var_name)

                self.datatable.delete_variables(variable_names)

                model = VariablesModel(self.datatable)
                self.tableView.model().setSourceModel(model)
                self.tableView.resizeColumnsToContents()

    def _freeze_removal(self) -> None:
        if self.outliers_widget_ui.radioButtonRemoveOutliers.isChecked():
            if (
                QMessageBox.question(
                    self,
                    "TSE Analytics",
                    "Do you want to freeze outliers removal? This step is irreversible!",
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                self.datatable.freeze_outliers_removal()

    def minimumSizeHint(self):
        return QSize(200, 100)
