# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'raw_data_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGroupBox,
    QHBoxLayout, QHeaderView, QListWidget, QListWidgetItem,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)
import resources_rc

class Ui_RawDataWidget(object):
    def setupUi(self, RawDataWidget):
        if not RawDataWidget.objectName():
            RawDataWidget.setObjectName(u"RawDataWidget")
        self.horizontalLayout = QHBoxLayout(RawDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxTables = QGroupBox(RawDataWidget)
        self.groupBoxTables.setObjectName(u"groupBoxTables")
        self.verticalLayout = QVBoxLayout(self.groupBoxTables)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.listWidgetTables = QListWidget(self.groupBoxTables)
        self.listWidgetTables.setObjectName(u"listWidgetTables")
        self.listWidgetTables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.listWidgetTables)


        self.horizontalLayout.addWidget(self.groupBoxTables)

        self.groupBoxData = QGroupBox(RawDataWidget)
        self.groupBoxData.setObjectName(u"groupBoxData")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxData.sizePolicy().hasHeightForWidth())
        self.groupBoxData.setSizePolicy(sizePolicy)
        self.tableLayout = QVBoxLayout(self.groupBoxData)
        self.tableLayout.setSpacing(0)
        self.tableLayout.setObjectName(u"tableLayout")
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.groupBoxData)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.tableLayout.addWidget(self.tableView)


        self.horizontalLayout.addWidget(self.groupBoxData)

        self.groupBoxAnimals = QGroupBox(RawDataWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(RawDataWidget)

        QMetaObject.connectSlotsByName(RawDataWidget)
    # setupUi

    def retranslateUi(self, RawDataWidget):
        self.groupBoxTables.setTitle(QCoreApplication.translate("RawDataWidget", u"Data Tables", None))
        self.groupBoxData.setTitle(QCoreApplication.translate("RawDataWidget", u"Data", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("RawDataWidget", u"Animals", None))
        pass
    # retranslateUi

