from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QMessageBox,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.models.aggregation_combo_box_delegate import AggregationComboBoxDelegate
from tse_analytics.core.models.variables_model import VariablesModel
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values
from tse_analytics.modules.phenomaster.data.variables_helper import cleanup_variables
from tse_analytics.views.general.variables.add_variable_dialog import AddVariableDialog


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

        self.outliersModeComboBox = QComboBox()
        self.outliersModeComboBox.addItems(list(OutliersMode))
        self.outliersModeComboBox.currentTextChanged.connect(self._outliers_mode_changed)
        toolbar.addWidget(self.outliersModeComboBox)

        self.outliersCoefficientSpinBox = QDoubleSpinBox()
        self.outliersCoefficientSpinBox.valueChanged.connect(self._outliers_coefficient_changed)
        toolbar.addWidget(self.outliersCoefficientSpinBox)

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
            self.outliersCoefficientSpinBox.setValue(1.5)
            self.outliersModeComboBox.setCurrentText(OutliersMode.OFF)
        else:
            self.datatable = message.datatable
            model = VariablesModel(self.datatable)
            self.tableView.model().setSourceModel(model)
            self.tableView.resizeColumnsToContents()
            self.outliersCoefficientSpinBox.setValue(self.datatable.dataset.outliers_settings.coefficient)
            self.outliersModeComboBox.setCurrentText(self.datatable.dataset.outliers_settings.mode)

    def _outliers_mode_changed(self, value: str):
        if self.datatable is not None:
            outliers_settings = self.datatable.dataset.outliers_settings
            outliers_settings.mode = OutliersMode(self.outliersModeComboBox.currentText())
            self.datatable.dataset.apply_outliers(outliers_settings)

    def _outliers_coefficient_changed(self, value: float):
        if self.datatable is not None:
            outliers_settings = self.datatable.dataset.outliers_settings
            outliers_settings.coefficient = self.outliersCoefficientSpinBox.value()
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

    def minimumSizeHint(self):
        return QSize(200, 100)
