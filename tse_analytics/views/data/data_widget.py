from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QTabWidget, QComboBox, QLabel

from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage, \
    BinningAppliedMessage, DataChangedMessage
from tse_analytics.views.data.plot_view_widget import PlotViewWidget
from tse_analytics.views.data.table_view_widget import TableViewWidget


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
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)
        messenger.subscribe(self, BinningAppliedMessage, self._on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self._on_data_changed)

    def clear(self):
        self.table_view_widget.clear()
        self.plot_view_widget.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.plot_view_widget.set_variables(message.data.variables)
        self._assign_data()

    def _on_binning_applied(self, message: BinningAppliedMessage):
        self._assign_data()

    def _on_data_changed(self, message: DataChangedMessage):
        self._assign_data()

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def _assign_data(self):
        df = Manager.data.get_current_df()
        self.table_view_widget.set_data(df)
        self.plot_view_widget.set_data(df)

    def _mode_current_text_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))
        self._assign_data()

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
        mode_combo_box.addItems([e.value for e in GroupingMode])
        mode_combo_box.currentTextChanged.connect(self._mode_current_text_changed)
        toolbar.addWidget(mode_combo_box)

        return toolbar
