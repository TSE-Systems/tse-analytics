from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QInputDialog, QHeaderView

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.models.time_phases_model import TimePhasesModel
from tse_analytics.views.settings.time_settings_widget_ui import Ui_TimeSettingsWidget
from tse_datatools.analysis.time_cycles_params import TimeCyclesParams
from tse_datatools.data.time_phase import TimePhase


class TimeSettingsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_TimeSettingsWidget()
        self.ui.setupUi(self)

        self.ui.checkBoxApply.stateChanged.connect(self.__apply_time_cycles_changed)
        self.ui.timeEditLightCycleStart.editingFinished.connect(self.__light_cycle_start_changed)
        self.ui.timeEditDarkCycleStart.editingFinished.connect(self.__dark_cycle_start_changed)

        self.ui.toolButtonAddPhase.clicked.connect(self.__add_time_phase)
        self.ui.toolButtonDeletePhase.clicked.connect(self.__delete_time_phase)

        self.time_phases_model = TimePhasesModel([])
        self.ui.tableViewTimePhases.setModel(self.time_phases_model)

        header = self.ui.tableViewTimePhases.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_clear_data(self, message: ClearDataMessage):
        self.time_phases_model.items = []
        # Trigger refresh.
        self.time_phases_model.layoutChanged.emit()

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.time_phases_model.items = message.data.time_phases
        # Trigger refresh.
        self.time_phases_model.layoutChanged.emit()

    def __apply_time_cycles_changed(self, value: int):
        self.__time_cycles_params_changed()

    def __light_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    def __dark_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    def __add_time_phase(self):
        if Manager.data.selected_dataset is not None:
            text, result = QInputDialog.getText(self, "Add Time Phase", "Please enter unique phase name:")
            if result:
                start_timestamp = datetime.now()
                if len(self.time_phases_model.items) > 0:
                    start_timestamp = self.time_phases_model.items[-1].start_timestamp
                    start_timestamp = start_timestamp + timedelta(hours=1)
                elif len(Manager.data.selected_dataset.original_df) > 0:
                    start_timestamp = Manager.data.selected_dataset.original_df["DateTime"][0]
                time_phase = TimePhase(name=text, start_timestamp=start_timestamp)
                self.time_phases_model.add_time_phase(time_phase)

    def __delete_time_phase(self):
        if Manager.data.selected_dataset is not None:
            indexes = self.ui.tableViewTimePhases.selectedIndexes()
            if indexes:
                # Indexes is a single-item list in single-select mode.
                index = indexes[0]
                self.time_phases_model.delete_time_phase(index)
                # Clear the selection (as it is no longer valid).
                self.ui.tableViewTimePhases.clearSelection()

    def __time_cycles_params_changed(self):
        apply = self.ui.checkBoxApply.isChecked()
        light_cycle_start = self.ui.timeEditLightCycleStart.time().toPython()
        dark_cycle_start = self.ui.timeEditDarkCycleStart.time().toPython()
        params = TimeCyclesParams(apply, light_cycle_start, dark_cycle_start)
        Manager.data.time_cycles_params = params

    def minimumSizeHint(self):
        return QSize(200, 40)
