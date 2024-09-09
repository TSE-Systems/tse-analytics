from functools import partial

from PySide6.QtCore import QItemSelection, QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Animal
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

        pal = self.ui.tableView.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.ui.tableView.setPalette(pal)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)
        self.ui.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.ui.tableView.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.ui.toolButtonCheckAll.clicked.connect(partial(self._set_animals_state, True))
        self.ui.toolButtonUncheckAll.clicked.connect(partial(self._set_animals_state, False))

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = AnimalsModel(list(message.data.animals.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.ui.tableView.model()
        model = proxy_model.sourceModel()
        selected_animals: list[Animal] = []
        for index in self.ui.tableView.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                animal = model.items[row]
                selected_animals.append(animal)
        Manager.data.set_selected_animals(selected_animals)

    def _set_animals_state(self, state: bool) -> None:
        if Manager.data.selected_dataset is None:
            return

        self.ui.tableView.model().beginResetModel()
        for animal in Manager.data.selected_dataset.animals.values():
            animal.enabled = state
        self.ui.tableView.model().endResetModel()

    def minimumSizeHint(self):
        return QSize(300, 100)
