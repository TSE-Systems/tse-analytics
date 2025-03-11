from functools import partial

from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QWidget, QVBoxLayout, QTableView, QAbstractItemView, QInputDialog, QLineEdit, \
    QMessageBox

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.models.animals_model import AnimalsModel


class AnimalsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.dataset: Dataset | None = None

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar(
            "Animals Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.check_all_action = toolbar.addAction("Check All")
        self.check_all_action.triggered.connect(partial(self._set_animals_state, True))

        self.uncheck_all_action = toolbar.addAction("Uncheck All")
        self.uncheck_all_action.triggered.connect(partial(self._set_animals_state, False))

        toolbar.addSeparator()
        toolbar.addAction(QIcon(":/icons/icons8-add-16.png"), "Add property").triggered.connect(self._add_property)

        self.layout.addWidget(toolbar)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.tableView = QTableView(
            self,
            sortingEnabled=True,
        )
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.setModel(proxy_model)
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.layout.addWidget(self.tableView)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.dataset = message.dataset
        if self.dataset is None:
            self.tableView.model().setSourceModel(None)
        else:
            self._set_model()

    def _set_model(self):
        model = AnimalsModel(self.dataset)
        self.tableView.model().setSourceModel(model)
        self.tableView.resizeColumnsToContents()

    def _set_animals_state(self, state: bool) -> None:
        if self.dataset is None:
            return

        self.tableView.model().beginResetModel()
        for animal in self.dataset.animals.values():
            animal.enabled = state
        self.tableView.model().endResetModel()
        messaging.broadcast(messaging.DataChangedMessage(self, self.dataset))

    def _add_property(self) -> None:
        if self.dataset is None:
            return

        name, ok = QInputDialog.getText(
            self,
            "Enter property name",
            "Name",
            QLineEdit.EchoMode.Normal,
            "",
        )
        if ok:
            if name == "":
                QMessageBox.warning(self, "Warning", "Property name cannot be empty.")
                return
            if len(self.dataset.animals) > 0:
                animal_properties = next(iter(self.dataset.animals.values())).properties
                if name in animal_properties:
                    QMessageBox.warning(self, "Warning", "Property name already exists.")
                    return
            # Add new property to all animals
            for animal in self.dataset.animals.values():
                animal.properties[name] = 0.0

            self._set_model()


    def minimumSizeHint(self):
        return QSize(300, 100)
