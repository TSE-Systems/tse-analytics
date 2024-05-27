# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_table_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QSizePolicy, QSpacerItem, QTableView, QToolButton,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_DataTableWidget(object):
    def setupUi(self, DataTableWidget):
        if not DataTableWidget.objectName():
            DataTableWidget.setObjectName(u"DataTableWidget")
        self._2 = QVBoxLayout(DataTableWidget)
        self._2.setObjectName(u"_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonResizeColumns = QToolButton(DataTableWidget)
        self.toolButtonResizeColumns.setObjectName(u"toolButtonResizeColumns")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-resize-horizontal-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonResizeColumns.setIcon(icon)
        self.toolButtonResizeColumns.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonResizeColumns)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self._2.addLayout(self.horizontalLayout)

        self.tableView = QTableView(DataTableWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self._2.addWidget(self.tableView)


        self.retranslateUi(DataTableWidget)

        QMetaObject.connectSlotsByName(DataTableWidget)
    # setupUi

    def retranslateUi(self, DataTableWidget):
        self.toolButtonResizeColumns.setText(QCoreApplication.translate("DataTableWidget", u"Resize Columns", None))
        pass
    # retranslateUi

