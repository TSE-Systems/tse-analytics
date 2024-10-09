from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QToolBar, QWidget

from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.aggregation_combo_box_delegate import AggregationComboBoxDelegate
from tse_analytics.core.models.variables_model import VariablesModel
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.selection.variables.variables_widget_ui import Ui_VariablesWidget


class VariablesWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

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

        self.layout().insertWidget(0, toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.ui.tableView.setItemDelegateForColumn(2, AggregationComboBoxDelegate(self.ui.tableView))

        self.dataset: Dataset | None = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.dataset is None:
            self.dataset = None
            self.ui.tableView.model().setSourceModel(None)
            self.outliersCoefficientSpinBox.setValue(1.5)
            self.outliersModeComboBox.setCurrentText(OutliersMode.OFF)
        else:
            self.dataset = message.dataset
            model = VariablesModel(list(self.dataset.variables.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()
            self.outliersCoefficientSpinBox.setValue(self.dataset.outliers_settings.coefficient)
            self.outliersModeComboBox.setCurrentText(self.dataset.outliers_settings.mode)

    def _outliers_mode_changed(self, value: str):
        if self.dataset is not None:
            outliers_settings = self.dataset.outliers_settings
            outliers_settings.mode = OutliersMode(self.outliersModeComboBox.currentText())
            Manager.data.apply_outliers(outliers_settings)

    def _outliers_coefficient_changed(self, value: float):
        if self.dataset is not None:
            outliers_settings = self.dataset.outliers_settings
            outliers_settings.coefficient = self.outliersCoefficientSpinBox.value()
            Manager.data.apply_outliers(outliers_settings)

    def minimumSizeHint(self):
        return QSize(200, 100)
