from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import QSize, Qt, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QVBoxLayout,
    QWidget,
    QTimeEdit,
    QGroupBox,
    QScrollArea,
)

from tse_analytics.core.manager import Manager
from tse_datatools.analysis.time_cycles_params import TimeCyclesParams


class TimePhasesWidget(QScrollArea):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWidgetResizable(True)

        widget = QWidget(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        widget.setLayout(layout)

        time_cycles_groupbox = QGroupBox("Light/Dark Cycles")
        time_cycles_layout = QVBoxLayout()

        self.apply_time_cycles_checkbox = QCheckBox("Apply")
        self.apply_time_cycles_checkbox.stateChanged.connect(self.__apply_time_cycles_changed)
        time_cycles_layout.addWidget(self.apply_time_cycles_checkbox)

        time_cycles_layout.addWidget(QLabel("Light cycle starts:"))
        self.light_cycle_start_edit = QTimeEdit()
        self.light_cycle_start_edit.setTime(QTime(7, 0))
        self.light_cycle_start_edit.editingFinished.connect(self.__light_cycle_start_changed)
        time_cycles_layout.addWidget(self.light_cycle_start_edit)

        time_cycles_layout.addWidget(QLabel("Dark cycle starts:"))
        self.dark_cycle_start_edit = QTimeEdit()
        self.dark_cycle_start_edit.setTime(QTime(19, 0))
        self.dark_cycle_start_edit.editingFinished.connect(self.__dark_cycle_start_changed)
        time_cycles_layout.addWidget(self.dark_cycle_start_edit)

        time_cycles_groupbox.setLayout(time_cycles_layout)
        layout.addWidget(time_cycles_groupbox)

        self.setWidget(widget)

    @QtCore.Slot(int)
    def __apply_time_cycles_changed(self, value: int):
        self.__time_cycles_params_changed()

    @QtCore.Slot()
    def __light_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    @QtCore.Slot()
    def __dark_cycle_start_changed(self):
        self.__time_cycles_params_changed()

    def __time_cycles_params_changed(self):
        apply = self.apply_time_cycles_checkbox.isChecked()
        light_cycle_start = self.light_cycle_start_edit.time().toPython()
        dark_cycle_start = self.dark_cycle_start_edit.time().toPython()
        params = TimeCyclesParams(apply, light_cycle_start, dark_cycle_start)
        Manager.data.time_cycles_params = params

    def minimumSizeHint(self):
        return QSize(200, 40)
