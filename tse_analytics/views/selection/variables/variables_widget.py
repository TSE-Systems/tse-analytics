from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QToolBar, QWidget, QVBoxLayout, QTableView, QAbstractItemView, \
    QMessageBox

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.models.aggregation_combo_box_delegate import AggregationComboBoxDelegate
from tse_analytics.core.models.variables_model import VariablesModel
from tse_analytics.modules.phenomaster.data.predefined_variables import assign_predefined_values


class VariablesWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.dataset: Dataset | None = None

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar(
            "Variables Toolbar",
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
        toolbar.addAction(QIcon(":/icons/icons8-remove-16.png"), "Delete").triggered.connect(self._delete_variable)

        self.layout.addWidget(toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

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
        self.tableView.setModel(proxy_model)
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tableView.setItemDelegateForColumn(2, AggregationComboBoxDelegate(self.tableView))

        self.layout.addWidget(self.tableView)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self.dataset = None
            self.tableView.model().setSourceModel(None)
            self.outliersCoefficientSpinBox.setValue(1.5)
            self.outliersModeComboBox.setCurrentText(OutliersMode.OFF)
        else:
            self.dataset = message.dataset
            model = VariablesModel(list(self.dataset.variables.values()), self.dataset)
            self.tableView.model().setSourceModel(model)
            self.tableView.resizeColumnsToContents()
            self.outliersCoefficientSpinBox.setValue(self.dataset.outliers_settings.coefficient)
            self.outliersModeComboBox.setCurrentText(self.dataset.outliers_settings.mode)

    def _outliers_mode_changed(self, value: str):
        if self.dataset is not None:
            outliers_settings = self.dataset.outliers_settings
            outliers_settings.mode = OutliersMode(self.outliersModeComboBox.currentText())
            self.dataset.apply_outliers(outliers_settings)

    def _outliers_coefficient_changed(self, value: float):
        if self.dataset is not None:
            outliers_settings = self.dataset.outliers_settings
            outliers_settings.coefficient = self.outliersCoefficientSpinBox.value()
            self.dataset.apply_outliers(outliers_settings)

    def _reset_variables(self):
        if self.dataset is not None:
            self.dataset.variables = assign_predefined_values(self.dataset.variables)
            model = VariablesModel(list(self.dataset.variables.values()), self.dataset)
            self.tableView.model().setSourceModel(model)
            self.tableView.resizeColumnsToContents()

    def _delete_variable(self) -> None:
        if self.dataset is None:
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

                self.dataset.delete_variables(variable_names)

                model = VariablesModel(list(self.dataset.variables.values()), self.dataset)
                self.tableView.model().setSourceModel(model)
                self.tableView.resizeColumnsToContents()

    def minimumSizeHint(self):
        return QSize(200, 100)
