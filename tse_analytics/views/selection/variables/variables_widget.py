from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QWidget, QToolBar, QComboBox, QDoubleSpinBox

from tse_analytics.core.data.outliers import OutliersMode, OutliersParams
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.variables_model import VariablesModel
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
        self.outliersModeComboBox.addItems([e.value for e in OutliersMode])
        self.outliersModeComboBox.currentTextChanged.connect(self._outliers_mode_changed)
        toolbar.addWidget(self.outliersModeComboBox)

        self.outliersCoefficientSpinBox = QDoubleSpinBox()
        self.outliersCoefficientSpinBox.setValue(Manager.data.outliers_params.coefficient)
        self.outliersCoefficientSpinBox.valueChanged.connect(self._outliers_coefficient_changed)
        toolbar.addWidget(self.outliersCoefficientSpinBox)

        self.layout().insertWidget(0, toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = VariablesModel(list(message.data.variables.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def _outliers_mode_changed(self, value: str):
        self._outliers_params_changed()

    def _outliers_coefficient_changed(self, value: float):
        self._outliers_params_changed()

    def _outliers_params_changed(self):
        mode = OutliersMode(self.outliersModeComboBox.currentText())
        outliers_coefficient = self.outliersCoefficientSpinBox.value()
        outliers_params = OutliersParams(mode, outliers_coefficient)
        Manager.data.apply_outliers(outliers_params)

    def minimumSizeHint(self):
        return QSize(200, 100)
