from functools import partial

from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QToolBar, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.models.animals_model import AnimalsModel
from tse_analytics.views.selection.animals.animals_widget_ui import Ui_AnimalsWidget


class AnimalsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_AnimalsWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        toolbar = QToolBar("Animals Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.check_all_action = toolbar.addAction("Check All")
        self.check_all_action.triggered.connect(partial(self._set_animals_state, True))

        self.uncheck_all_action = toolbar.addAction("Uncheck All")
        self.uncheck_all_action.triggered.connect(partial(self._set_animals_state, False))

        self.layout().insertWidget(0, toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.dataset: Dataset | None = None

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.dataset = message.dataset
        if self.dataset is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = AnimalsModel(message.dataset)
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def _set_animals_state(self, state: bool) -> None:
        if self.dataset is None:
            return

        self.ui.tableView.model().beginResetModel()
        for animal in self.dataset.animals.values():
            animal.enabled = state
        self.ui.tableView.model().endResetModel()
        messaging.broadcast(messaging.DataChangedMessage(self, self.dataset))

    def minimumSizeHint(self):
        return QSize(300, 100)
