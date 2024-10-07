from functools import partial

from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QWidget, QToolBar

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.animals_model import AnimalsModel
from tse_analytics.views.selection.animals.animals_widget_ui import Ui_AnimalsWidget


class AnimalsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_AnimalsWidget()
        self.ui.setupUi(self)

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

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.dataset is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = AnimalsModel(list(message.dataset.animals.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def _set_animals_state(self, state: bool) -> None:
        if Manager.data.selected_dataset is None:
            return

        self.ui.tableView.model().beginResetModel()
        for animal in Manager.data.selected_dataset.animals.values():
            animal.enabled = state
        self.ui.tableView.model().endResetModel()
        Manager.data.set_selected_animals()

    def minimumSizeHint(self):
        return QSize(300, 100)
