# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'intellicage_raw_data_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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

class Ui_IntelliCageRawDataWidget(object):
    def setupUi(self, IntelliCageRawDataWidget):
        if not IntelliCageRawDataWidget.objectName():
            IntelliCageRawDataWidget.setObjectName(u"IntelliCageRawDataWidget")
        self.horizontalLayout = QHBoxLayout(IntelliCageRawDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxTables = QGroupBox(IntelliCageRawDataWidget)
        self.groupBoxTables.setObjectName(u"groupBoxTables")
        self.verticalLayout = QVBoxLayout(self.groupBoxTables)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetTables = QListWidget(self.groupBoxTables)
        self.listWidgetTables.setObjectName(u"listWidgetTables")
        self.listWidgetTables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.listWidgetTables)


        self.horizontalLayout.addWidget(self.groupBoxTables)

        self.tableView = QTableView(IntelliCageRawDataWidget)
        self.tableView.setObjectName(u"tableView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.horizontalLayout.addWidget(self.tableView)

        self.groupBoxCages = QGroupBox(IntelliCageRawDataWidget)
        self.groupBoxCages.setObjectName(u"groupBoxCages")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxCages)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetCages = QListWidget(self.groupBoxCages)
        self.listWidgetCages.setObjectName(u"listWidgetCages")
        self.listWidgetCages.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetCages.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetCages)


        self.horizontalLayout.addWidget(self.groupBoxCages)


        self.retranslateUi(IntelliCageRawDataWidget)

        QMetaObject.connectSlotsByName(IntelliCageRawDataWidget)
    # setupUi

    def retranslateUi(self, IntelliCageRawDataWidget):
        self.groupBoxTables.setTitle(QCoreApplication.translate("IntelliCageRawDataWidget", u"Data Tables", None))
        self.groupBoxCages.setTitle(QCoreApplication.translate("IntelliCageRawDataWidget", u"Cages", None))
        pass
    # retranslateUi

