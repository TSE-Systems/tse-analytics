from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QToolBar, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.models.aggregation_combo_box_delegate import AggregationComboBoxDelegate
from tse_analytics.core.models.variables_model import VariablesModel
from tse_analytics.core.predefined_variables import assign_predefined_values
from tse_analytics.views.selection.variables.variables_widget_ui import Ui_VariablesWidget


class VariablesWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.ui = Ui_VariablesWidget()
        self.ui.setupUi(self)

        toolbar = QToolBar("Variables Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.outliersModeComboBox = QComboBox()
        self.outliersModeComboBox.addItems(list(OutliersMode))
        self.outliersModeComboBox.currentTextChanged.connect(self._outliers_mode_changed)
        toolbar.addWidget(self.outliersModeComboBox)

        self.outliersCoefficientSpinBox = QDoubleSpinBox()
        self.outliersCoefficientSpinBox.valueChanged.connect(self._outliers_coefficient_changed)
        toolbar.addWidget(self.outliersCoefficientSpinBox)

        toolbar.addAction("Reset").triggered.connect(self._reset_variables)

        self.layout().insertWidget(0, toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.ui.tableView.setItemDelegateForColumn(2, AggregationComboBoxDelegate(self.ui.tableView))

        self.dataset: Dataset | None = None

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self.dataset = None
            self.ui.tableView.model().setSourceModel(None)
            self.outliersCoefficientSpinBox.setValue(1.5)
            self.outliersModeComboBox.setCurrentText(OutliersMode.OFF)
        else:
            self.dataset = message.dataset
            model = VariablesModel(list(self.dataset.variables.values()), self.dataset)
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()
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
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def minimumSizeHint(self):
        return QSize(200, 100)
