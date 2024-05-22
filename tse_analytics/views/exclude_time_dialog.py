from datetime import datetime, timedelta

from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.exclude_time_dialog_ui import Ui_ExcludeTimeDialog


class ExcludeTimeDialog(QDialog, Ui_ExcludeTimeDialog):
    def __init__(self, min_datetime: datetime, max_datetime: datetime, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        delta = timedelta(seconds=1)

        self.dateTimeEditStart.setMinimumDateTime(min_datetime - delta)
        self.dateTimeEditStart.setMaximumDateTime(max_datetime + delta)
        self.dateTimeEditStart.setDateTime(min_datetime)

        self.dateTimeEditEnd.setMinimumDateTime(min_datetime - delta)
        self.dateTimeEditEnd.setMaximumDateTime(max_datetime + delta)
        self.dateTimeEditEnd.setDateTime(max_datetime)
