from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QCloseEvent, QKeyEvent, QIcon
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QToolBar, QTabWidget

from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.views.intellicage_data_widget import IntelliCageDataWidget


class IntelliCageDialog(QDialog):
    def __init__(self, dataset: IntelliCageDataset, parent: QWidget | None = None):
        super().__init__(
            parent,
            sizeGripEnabled=True,
        )

        self.setWindowTitle("IntelliCage")
        self.resize(900, 600)
        self.layout = QVBoxLayout(self)

        self.dataset = dataset

        # Setup toolbar
        toolbar = QToolBar(
            "IntelliCage Dialog Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
        )
        self.layout.addWidget(toolbar)

        self.data_widget = IntelliCageDataWidget(self.dataset.intellicage_data, self)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.data_widget, "Raw Data")
        self.layout.addWidget(self.tabWidget)

        settings = QSettings()
        self.restoreGeometry(settings.value("IntelliCageDialog/Geometry"))

    def _resize_columns_width(self):
        worker = Worker(self.data_widget.resize_columns)  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("IntelliCageDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
