import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.data.report import Report
from tse_analytics.core.models.tree_item import TreeItem


class ReportTreeItem(TreeItem):
    def __init__(self, report: Report):
        super().__init__(report.name)

        self._report = weakref.ref(report)

    @property
    def report(self):
        return self._report()

    @property
    def icon(self):
        return QIcon(":/icons/icons8-report-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return f"Created on {self.report.timestamp}"
