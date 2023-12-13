from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel, QItemSelection, QSize
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.models.animals_model import AnimalsModel
from tse_analytics.views.selection.animals.animals_widget_ui import Ui_AnimalsWidget
from tse_datatools.data.animal import Animal


class AnimalsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
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
        self.ui.tableView.selectionModel().selectionChanged.connect(self.__on_selection_changed)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.model().setSourceModel(None)
        else:
            model = AnimalsModel(list(message.data.animals.values()))
            self.ui.tableView.model().setSourceModel(model)
            self.ui.tableView.resizeColumnsToContents()

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
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

    def minimumSizeHint(self):
        return QSize(200, 40)
