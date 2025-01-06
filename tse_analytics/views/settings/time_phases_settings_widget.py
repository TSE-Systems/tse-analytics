import pandas as pd
from PySide6.QtWidgets import QHeaderView, QInputDialog, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import TimePhase
from tse_analytics.core.models.time_phases_model import TimePhasesModel
from tse_analytics.views.settings.time_phases_settings_widget_ui import Ui_TimePhasesSettingsWidget


class TimePhasesSettingsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TimePhasesSettingsWidget()
        self.ui.setupUi(self)

        self.dataset: Dataset | None = None

        self.ui.toolButtonAddPhase.clicked.connect(self._add_time_phase)
        self.ui.toolButtonDeletePhase.clicked.connect(self._delete_time_phase)

        self.time_phases_model = TimePhasesModel(self.dataset)
        self.ui.tableViewTimePhases.setModel(self.time_phases_model)

        header = self.ui.tableViewTimePhases.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def set_data(self, dataset: Dataset):
        self.dataset = dataset
        self.time_phases_model.dataset = self.dataset
        self.time_phases_model.items = self.dataset.binning_settings.time_phases_settings.time_phases
        # Trigger refresh.
        self.time_phases_model.layoutChanged.emit()

    def clear(self):
        self.time_phases_model.items = []
        # Trigger refresh.
        self.time_phases_model.layoutChanged.emit()

    def _add_time_phase(self):
        if self.dataset is None:
            return
        text, result = QInputDialog.getText(self, "Add Time Phase", "Please enter unique phase name:")
        if result:
            start_timestamp = pd.Timedelta("0 days 00:00:00")
            if len(self.time_phases_model.items) > 0:
                start_timestamp = self.time_phases_model.items[-1].start_timestamp
                start_timestamp = start_timestamp + pd.to_timedelta(1, unit="hours")
            time_phase = TimePhase(name=text, start_timestamp=start_timestamp)
            self.time_phases_model.add_time_phase(time_phase)

    def _delete_time_phase(self):
        if self.dataset is None:
            return
        indexes = self.ui.tableViewTimePhases.selectedIndexes()
        if indexes:
            # Indexes is a single-item list in single-select mode.
            index = indexes[0]
            self.time_phases_model.delete_time_phase(index)
            # Clear the selection (as it is no longer valid).
            self.ui.tableViewTimePhases.clearSelection()
