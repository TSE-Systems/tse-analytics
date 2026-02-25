from dataclasses import dataclass

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget
from tse_analytics.core.workers import TaskManager, Worker
from tse_analytics.modules.intellicage.toolbox.transitions.processor import (
    IntelliCageTransitionsResult,
    get_intellicage_transitions_result,
)
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.views.misc.report_edit import ReportEdit


@dataclass
class TransitionsWidgetSettings:
    alpha = 0.05


@toolbox_plugin(
    category="IntelliCage", label="Transitions", icon=":/icons/icons8-transition-both-directions-16.png", order=0
)
class TransitionsWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: TransitionsWidgetSettings = settings.value(self.__class__.__name__, TransitionsWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Transitions"

        self.datatable = datatable
        self._toast = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.update_action = toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update")
        self.update_action.triggered.connect(self._update)
        toolbar.addSeparator()

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            TransitionsWidgetSettings(),
        )

    def _update(self):
        self.report_view.clear()

        self.update_action.setEnabled(False)

        self._toast = make_toast(self, self.title, "Processing...")
        self._toast.show()

        columns = ["Timedelta", "Animal", "Corner"]
        df = self.datatable.df[columns]

        animal_ids = [animal.id for animal in self.datatable.dataset.animals.values() if animal.enabled]

        worker = Worker(
            get_intellicage_transitions_result,
            self.datatable.dataset,
            df,
            animal_ids,
            0.05,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: IntelliCageTransitionsResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self._toast.hide()
        self.update_action.setEnabled(True)

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.report_view.toHtml(),
                )
            )
