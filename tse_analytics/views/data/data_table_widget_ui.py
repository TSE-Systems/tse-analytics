# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_table_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
        DataTableWidget.resize(489, 630)
        self.verticalLayout = QVBoxLayout(DataTableWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonEnableSorting = QToolButton(DataTableWidget)
        self.toolButtonEnableSorting.setObjectName(u"toolButtonEnableSorting")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-sorting-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonEnableSorting.setIcon(icon)
        self.toolButtonEnableSorting.setCheckable(True)
        self.toolButtonEnableSorting.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonEnableSorting)

        self.toolButtonResizeColumns = QToolButton(DataTableWidget)
        self.toolButtonResizeColumns.setObjectName(u"toolButtonResizeColumns")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-resize-horizontal-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonResizeColumns.setIcon(icon1)
        self.toolButtonResizeColumns.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonResizeColumns)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableView = QTableView(DataTableWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(DataTableWidget)

        QMetaObject.connectSlotsByName(DataTableWidget)
    # setupUi

    def retranslateUi(self, DataTableWidget):
        DataTableWidget.setWindowTitle(QCoreApplication.translate("DataTableWidget", u"Form", None))
        self.toolButtonEnableSorting.setText(QCoreApplication.translate("DataTableWidget", u"Enable Sorting", None))
        self.toolButtonResizeColumns.setText(QCoreApplication.translate("DataTableWidget", u"Resize Columns", None))
    # retranslateUi

