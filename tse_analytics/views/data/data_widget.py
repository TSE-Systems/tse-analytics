from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QTabWidget, QComboBox, QLabel

from tse_analytics.core.view_mode import ViewMode
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetChangedMessage, ViewModeChangedMessage, \
    BinningAppliedMessage, AnimalDataChangedMessage, GroupDataChangedMessage
from tse_analytics.views.data.plot_view_widget import PlotViewWidget
from tse_analytics.views.data.table_view_widget import TableViewWidget
from tse_datatools.analysis.processor import apply_time_binning


class DataWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

        self.tabWidget = QTabWidget(self)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.tabWidget)

        self.table_view_widget = TableViewWidget()
        self.tabWidget.addTab(self.table_view_widget, QIcon(":/icons/icons8-data-sheet-16.png"), "Table")

        self.plot_view_widget = PlotViewWidget()
        self.tabWidget.addTab(self.plot_view_widget, QIcon(":/icons/icons8-line-chart-16.png"), "Plot")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, BinningAppliedMessage, self._on_binning_applied)
        messenger.subscribe(self, AnimalDataChangedMessage, self._on_animal_data_changed)
        messenger.subscribe(self, GroupDataChangedMessage, self._on_group_data_changed)

    def clear(self):
        self.table_view_widget.clear()
        self.plot_view_widget.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.table_view_widget.set_data(message.data.df)

        self.plot_view_widget.set_variables(message.data.variables)
        self.plot_view_widget.set_data(message.data.df)

    def _on_binning_applied(self, message: BinningAppliedMessage):
        df = Manager.data.selected_dataset.df.copy()
        result = apply_time_binning(df, message.delta, message.unit, message.mode)
        self.table_view_widget.set_data(result)
        self.plot_view_widget.set_data(result)

    def _on_animal_data_changed(self, message: AnimalDataChangedMessage):
        self.table_view_widget.filter_animals(message.animals)
        self.plot_view_widget.filter_animals(message.animals)

    def _on_group_data_changed(self, message: GroupDataChangedMessage):
        self.table_view_widget.filter_groups(message.groups)
        self.plot_view_widget.filter_groups(message.groups)

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _mode_current_text_changed(self, text: str):
        mode = ViewMode(text)
        if mode == ViewMode.GROUPS and len(Manager.data.selected_dataset.groups) > 0:
            df = Manager.data.selected_dataset.calculate_groups_data()
            self.table_view_widget.set_data(df)
            self.plot_view_widget.set_data(df)
        elif mode == ViewMode.ANIMALS and len(Manager.data.selected_dataset.animals) > 0:
            df = Manager.data.selected_dataset.df
            self.table_view_widget.set_data(df)
            self.plot_view_widget.set_data(df)
        Manager.messenger.broadcast(ViewModeChangedMessage(self, mode))

    def _clear_selection(self):
        self.table_view_widget.clear_selection()
        self.plot_view_widget.clear_selection()

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        clear_selection_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Clear Selection", self)
        clear_selection_action.triggered.connect(self._clear_selection)
        toolbar.addAction(clear_selection_action)

        toolbar.addWidget(QLabel("Mode: "))

        mode_combo_box = QComboBox()
        mode_combo_box.addItems([e.value for e in ViewMode])
        mode_combo_box.currentTextChanged.connect(self._mode_current_text_changed)
        toolbar.addWidget(mode_combo_box)

        return toolbar
